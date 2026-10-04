def register_routes(app):
    @app.post("/extract_data/from_text")
    def extract_data_from_text() -> str:
        return "True"