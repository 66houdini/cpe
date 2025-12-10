from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models.scenario import ModelAssumption

bp = Blueprint('models', __name__, url_prefix='/api/models')


@bp.route('/assumptions', methods=['GET'])
def get_assumptions():
    """Get all model assumptions"""
    category = request.args.get('category')
    
    query = ModelAssumption.query
    if category:
        query = query.filter_by(category=category)
    
    assumptions = query.all()
    return jsonify([a.to_dict() for a in assumptions])


@bp.route('/assumptions/<int:id>', methods=['GET'])
def get_assumption(id):
    """Get single assumption"""
    assumption = ModelAssumption.query.get_or_404(id)
    return jsonify(assumption.to_dict())


@bp.route('/assumptions', methods=['POST'])
def create_assumption():
    """Create new model assumption"""
    data = request.get_json()
    
    if not data.get('name') or data.get('value') is None:
        return jsonify({'error': 'Name and value are required'}), 400
    
    assumption = ModelAssumption(
        name=data['name'],
        category=data.get('category'),
        value=data['value'],
        unit=data.get('unit'),
        description=data.get('description')
    )
    
    db.session.add(assumption)
    db.session.commit()
    
    return jsonify(assumption.to_dict()), 201


@bp.route('/assumptions/<int:id>', methods=['PUT'])
def update_assumption(id):
    """Update model assumption"""
    assumption = ModelAssumption.query.get_or_404(id)
    data = request.get_json()
    
    if 'name' in data:
        assumption.name = data['name']
    if 'category' in data:
        assumption.category = data['category']
    if 'value' in data:
        assumption.value = data['value']
    if 'unit' in data:
        assumption.unit = data['unit']
    if 'description' in data:
        assumption.description = data['description']
    
    db.session.commit()
    return jsonify(assumption.to_dict())


@bp.route('/assumptions/<int:id>', methods=['DELETE'])
def delete_assumption(id):
    """Delete model assumption"""
    assumption = ModelAssumption.query.get_or_404(id)
    db.session.delete(assumption)
    db.session.commit()
    return '', 204


@bp.route('/parameters', methods=['GET'])
def get_parameters():
    """Get available model parameters with metadata"""
    parameters = {
        'food_production_intensity': {
            'name': 'Food Production Intensity',
            'description': 'Level of agricultural intensification',
            'min': 0.0,
            'max': 1.0,
            'default': 0.5,
            'unit': 'normalized',
            'category': 'food',
            'impact': 'Higher values increase food output but also water and energy demands'
        },
        'renewable_energy_share': {
            'name': 'Renewable Energy Share',
            'description': 'Fraction of energy from renewable sources',
            'min': 0.0,
            'max': 1.0,
            'default': 0.3,
            'unit': 'fraction',
            'category': 'energy',
            'impact': 'Higher values reduce CO2 emissions and water stress from energy production'
        },
        'water_conservation_level': {
            'name': 'Water Conservation Level',
            'description': 'Effectiveness of water conservation measures',
            'min': 0.0,
            'max': 1.0,
            'default': 0.5,
            'unit': 'normalized',
            'category': 'water',
            'impact': 'Higher values reduce water demand across all sectors'
        },
        'population_growth': {
            'name': 'Population Growth Rate',
            'description': 'Annual population growth multiplier',
            'min': 0.95,
            'max': 1.10,
            'default': 1.01,
            'unit': 'annual rate',
            'category': 'demographic',
            'impact': 'Higher values increase demands across food, energy, and water'
        }
    }
    
    return jsonify(parameters)


@bp.route('/info', methods=['GET'])
def get_model_info():
    """Get model card information"""
    model_info = {
        'name': 'Food-Energy-Water Nexus Model',
        'version': '1.0.0',
        'description': 'An integrated system dynamics model for analyzing trade-offs '
                      'and synergies across food, energy, and water systems',
        'model_type': 'System Dynamics with Monte Carlo Uncertainty Quantification',
        'categories': ['food', 'energy', 'water', 'demographic'],
        'key_features': [
            'Cross-sectoral impact analysis',
            'Uncertainty quantification with confidence intervals',
            'Sensitivity analysis',
            'Multi-metric optimization visualization'
        ],
        'assumptions': [
            'Linear relationships for initial model (can be enhanced with feedback loops)',
            'Normal distribution for uncertainty propagation',
            'Fixed coefficients (can be calibrated with real data)',
            'Annual time steps for projections'
        ],
        'limitations': [
            'Simplified representation of complex systems',
            'Does not account for seasonal variations',
            'Limited spatial resolution',
            'Requires calibration with regional data'
        ],
        'use_cases': [
            'Policy scenario comparison',
            'Educational demonstrations',
            'Trade-off analysis',
            'Stakeholder engagement workshops'
        ],
        'authors': 'GRP 4 - Nexus Modeling Team',
        'last_updated': '2025-12-06'
    }
    
    return jsonify(model_info)
