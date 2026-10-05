import logging
import logging.config
import os
from datetime import datetime, timezone

from src.logging.logging_context import RequestContext

RESERVED_LOG_RECORD_KEYS = set(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime"}


class SafeExtraLogger(logging.Logger):
    def makeRecord(
            self,
            name: str,
            level: int,
            fn: str,
            lno: int,
            msg,
            args,
            exc_info,
            func=None,
            extra=None,
            sinfo=None,
    ) -> logging.LogRecord:
        if extra:
            extra = {self._normalize_extra_key(str(key)): value for key, value in extra.items()}
        return super().makeRecord(name, level, fn, lno, msg, args, exc_info, func, extra, sinfo)

    @staticmethod
    def _normalize_extra_key(key: str) -> str:
        normalized = key
        while normalized in RESERVED_LOG_RECORD_KEYS:
            normalized = f"extra_{normalized}"
        return normalized


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = RequestContext.current()
        record.request_id = context.request_id
        record.request_method = context.method
        record.request_path = context.path
        return True


class CompactFormatter(logging.Formatter):
    DISPLAY_ORDER_KEYS = ("event", "status_code", "duration_ms", "total")
    HIDDEN_KEYS = RESERVED_LOG_RECORD_KEYS | {
        "request_id",
        "request_method",
        "request_path",
    }

    @staticmethod
    def _to_text(value) -> str:
        text = str(value)
        return f"{text[:237]}..." if len(text) > 240 else text

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        message = f"{ts} {record.levelname:<8} {record.name}: {record.getMessage()}"

        no_value = RequestContext.NO_VALUE
        request_id = getattr(record, "request_id", no_value)
        if request_id != no_value:
            message = f"{message} [req={request_id}]"

        request_method = getattr(record, "request_method", no_value)
        request_path = getattr(record, "request_path", no_value)
        if request_method != no_value and request_path != no_value:
            message = f"{message} [{request_method} {request_path}]"

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in self.HIDDEN_KEYS
        }

        meta = []
        for key in self.DISPLAY_ORDER_KEYS:
            if key in extras and extras[key] is not None:
                meta.append(f"{key}={self._to_text(extras.pop(key))}")
        for key in sorted(extras.keys()):
            if extras[key] is not None:
                meta.append(f"{key}={self._to_text(extras[key])}")

        if meta:
            message = f"{message} | {' '.join(meta)}"
        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"

        return message


def setup_logging() -> logging.Logger:
    logging.setLoggerClass(SafeExtraLogger)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"request_context": {"()": RequestContextFilter}},
        "formatters": {"compact": {"()": CompactFormatter}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "compact",
                "filters": ["request_context"],
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": log_level, "handlers": ["console"]},
        "loggers": {
            "uvicorn": {"level": log_level, "handlers": ["console"], "propagate": False},
            "uvicorn.error": {"level": log_level, "handlers": ["console"], "propagate": False},
            "uvicorn.access": {"level": log_level, "handlers": ["console"], "propagate": False},
        },
    })

    logging.captureWarnings(True)
    return logging.getLogger()
