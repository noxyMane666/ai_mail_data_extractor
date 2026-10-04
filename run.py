import uvicorn

from src.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port=8080,
        reload=True
    )
else:
    application = app