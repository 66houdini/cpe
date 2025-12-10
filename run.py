from backend.app import create_app, db
from backend.models.scenario import Scenario, ScenarioComparison, ModelAssumption

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Scenario': Scenario, 'ScenarioComparison': ScenarioComparison}

if __name__ == '__main__':
    app.run(debug=True, port=5000)