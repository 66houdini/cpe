from backend.app import db
from backend.models.scenario import Scenario, ScenarioComparison, ModelAssumption
import os

# Flag to track if initialization has been done in this process
_initialized = False


def init_db_tables(app):
    """Initialize database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("✓ Database tables checked/created")


def seed_data_if_needed(app):
    """Seed database only if it's empty - with proper check"""
    global _initialized
    
    # Skip if already initialized in this process
    if _initialized:
        print("✓ Already initialized in this process, skipping")
        return
    
    with app.app_context():
        # Check if data already exists
        existing_count = ModelAssumption.query.count()
        if existing_count > 0:
            print(f"✓ Database already has {existing_count} assumptions, skipping seed")
            _initialized = True
            return
        
        print("Seeding database with initial data...")
        try:
            seed_assumptions()
            seed_example_scenarios()
            db.session.commit()
            print("✓ Database seeded successfully!")
            _initialized = True
        except Exception as e:
            db.session.rollback()
            print(f"Warning: Seeding failed (may already exist): {e}")
            _initialized = True


def seed_assumptions():
    """Seed database with model assumptions"""
    assumptions = [
        {
            'name': 'Food Water Coefficient',
            'category': 'food',
            'value': 2.5,
            'unit': 'liters/kg',
            'description': 'Water required per kg of food produced'
        },
        {
            'name': 'Food Energy Coefficient',
            'category': 'food',
            'value': 0.8,
            'unit': 'kWh/kg',
            'description': 'Energy required per kg of food produced'
        },
        {
            'name': 'Fossil Energy Water Coefficient',
            'category': 'energy',
            'value': 1.2,
            'unit': 'liters/kWh',
            'description': 'Water required per kWh of fossil energy'
        },
        {
            'name': 'Renewable Energy Water Coefficient',
            'category': 'energy',
            'value': 0.3,
            'unit': 'liters/kWh',
            'description': 'Water required per kWh of renewable energy'
        },
        {
            'name': 'CO2 Emission Factor',
            'category': 'energy',
            'value': 0.5,
            'unit': 'kg CO2/kWh',
            'description': 'CO2 emissions per kWh of fossil energy'
        },
        {
            'name': 'Base Water Availability',
            'category': 'water',
            'value': 10000,
            'unit': 'million liters',
            'description': 'Total water available in the system'
        },
        {
            'name': 'Water Conservation Effectiveness',
            'category': 'water',
            'value': 0.15,
            'unit': 'fraction',
            'description': 'Maximum reduction in water demand from conservation'
        },
        {
            'name': 'Domestic Water Base Demand',
            'category': 'water',
            'value': 1500,
            'unit': 'liters/person',
            'description': 'Base water demand for domestic use'
        }
    ]
    
    for assumption_data in assumptions:
        assumption = ModelAssumption(**assumption_data)
        db.session.add(assumption)
    
    print(f"  ✓ Added {len(assumptions)} model assumptions")


def seed_example_scenarios():
    """Seed database with example scenarios"""
    from backend.services.model_service import ModelService
    
    example_scenarios = [
        {
            'name': 'Business as Usual',
            'description': 'Baseline scenario with current policies and trends',
            'parameters': {
                'food_production_intensity': 0.5,
                'renewable_energy_share': 0.3,
                'water_conservation_level': 0.3,
                'population_growth': 1.02
            }
        },
        {
            'name': 'Green Transition',
            'description': 'Aggressive renewable energy adoption and water conservation',
            'parameters': {
                'food_production_intensity': 0.6,
                'renewable_energy_share': 0.8,
                'water_conservation_level': 0.7,
                'population_growth': 1.01
            }
        },
        {
            'name': 'Food Security Focus',
            'description': 'Maximize food production while managing resources',
            'parameters': {
                'food_production_intensity': 0.9,
                'renewable_energy_share': 0.5,
                'water_conservation_level': 0.6,
                'population_growth': 1.02
            }
        }
    ]
    
    model_service = ModelService()
    
    for scenario_data in example_scenarios:
        results = model_service.calculate_impacts(scenario_data['parameters'])
        scenario = Scenario(
            name=scenario_data['name'],
            description=scenario_data['description'],
            parameters=scenario_data['parameters'],
            results=results
        )
        db.session.add(scenario)
    
    print(f"  ✓ Added {len(example_scenarios)} example scenarios")


# For manual initialization (command line)
def init_db():
    """Complete database initialization (for manual use only)"""
    from backend.app import create_app
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    init_db_tables(app)
    seed_data_if_needed(app)


if __name__ == '__main__':
    init_db()
