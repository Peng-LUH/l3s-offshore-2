# src/l3s_offshore_2/api/simulation_petri_nets.py
"""API endpoints for example PNML models."""
import os
from flask import send_file, abort, Response, jsonify
from flask_restx import Namespace, Resource

# Robust: Hole das Projekt-Root-Verzeichnis aus der Umgebungsvariable oder gehe 2x nach oben
PROJECT_ROOT = os.environ.get("BASE_PATH") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS_DIR = os.path.join(
    PROJECT_ROOT,
    'datasets',
    'Process Discovery Contest 2023_1_all',
    'Models'
)

simulation_petri_nets_ns = Namespace('Simulation', description='Simulation Petri Net operations')

@simulation_petri_nets_ns.route('/example-models')
class ExampleModelsList(Resource):
    def get(self):
        """List all available example PNML model filenames."""
        try:
            files = [f for f in os.listdir(MODELS_DIR) if f.endswith('.pnml')]
            return files, 200
        except Exception as e:
            return {'message': str(e)}, 500

@simulation_petri_nets_ns.route('/example-models/<string:name>')
class ExampleModelContent(Resource):
    def get(self, name):
        """Return the PNML XML content for the given model name."""
        file_path = os.path.join(MODELS_DIR, name)
        if not os.path.isfile(file_path):
            abort(404, description='Model not found')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return Response(content, mimetype='text/plain')
        except Exception as e:
            return {'message': str(e)}, 500
