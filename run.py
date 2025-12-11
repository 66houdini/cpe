from backend.app import create_app, db
from backend.models.scenario import Scenario, ScenarioComparison, ModelAssumption

# Create the Flask app
app = create_app()

# Initialize database ONCE when the module is first loaded
# The _initialized flag in init_db prevents duplicate seeding
from backend.init_db import init_db_tables, seed_data_if_needed
init_db_tables(app)
seed_data_if_needed(app)
print("=== App Ready ===")

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Scenario': Scenario, 'ScenarioComparison': ScenarioComparison}

if __name__ == '__main__':
    app.run(debug=True, port=5000)