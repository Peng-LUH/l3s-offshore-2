"""Flask CLI/Application entry point."""
import os

from l3s_offshore_2 import create_app, db

app = create_app(os.getenv("FLASK_ENV", "development"))


@app.shell_context_processor
def shell():
    return {"db": db}

