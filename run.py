from backend.app import create_app, db
from backend.models.scenario import Scenario, ScenarioComparison, ModelAssumption
from backend.init_db import init_db_tables, seed_data_if_needed

# Create the Flask app
app = create_app()

# Auto-initialize database on startup
with app.app_context():
    try:
        print("=== Database Initialization ===")
        init_db_tables()
        seed_data_if_needed()
        print("=== Database Ready ===")
    except Exception as e:
        print(f"Warning: Database initialization issue: {e}")
        print("Continuing anyway - tables may already exist")

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Scenario': Scenario, 'ScenarioComparison': ScenarioComparison}

if __name__ == '__main__':
    app.run(debug=True, port=5000)