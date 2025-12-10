from backend.app import db
from datetime import datetime


class Scenario(db.Model):
    __tablename__ = 'scenarios'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Store parameters as JSON
    parameters = db.Column(db.JSON, nullable=False)
    # Example: {"food_production": 0.8, "renewable_energy": 0.6, "water_conservation": 0.7}

    # Results from model calculations
    results = db.Column(db.JSON)
    # Example: {"co2_emissions": 450, "water_usage": 1200, "food_security_index": 0.75}

    # Relationship to comparison groups
    comparisons = db.relationship('ScenarioComparison', back_populates='scenario', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'parameters': self.parameters,
            'results': self.results
        }


class ScenarioComparison(db.Model):
    __tablename__ = 'scenario_comparisons'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    scenario = db.relationship('Scenario', back_populates='comparisons')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'scenario_id': self.scenario_id,
            'created_at': self.created_at.isoformat()
        }


class ModelAssumption(db.Model):
    __tablename__ = 'model_assumptions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # 'food', 'energy', 'water'
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'value': self.value,
            'unit': self.unit,
            'description': self.description
        }