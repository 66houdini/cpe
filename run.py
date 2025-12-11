from backend.app import create_app, db
from backend.models.scenario import Scenario, ScenarioComparison, ModelAssumption

# Create the Flask app
app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Scenario': Scenario, 'ScenarioComparison': ScenarioComparison}

if __name__ == '__main__':
    # Only initialize database when running directly (development mode)
    # NOT when running with gunicorn
    from backend.init_db import init_db_tables, seed_data_if_needed
    
    with app.app_context():
        try:
            print("=== Database Initialization (Development Mode) ===")
            init_db_tables()
            seed_data_if_needed()
            print("=== Database Ready ===")
        except Exception as e:
            print(f"Warning: Database initialization issue: {e}")
    
    app.run(debug=True, port=5000)