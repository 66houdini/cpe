from flask import Blueprint, request, jsonify, Response
from backend.app import db
from backend.models.scenario import Scenario, ScenarioComparison
from backend.services.model_service import ModelService
from backend.services.cache_service import CacheService
from backend.services.export_service import ExportService
from backend.utils.explainer import ScenarioExplainer
from backend.utils.validators import ParameterValidator

bp = Blueprint('scenarios', __name__, url_prefix='/api/scenarios')


@bp.route('/', methods=['GET'])
def get_scenarios():
    """Get all scenarios"""
    scenarios = Scenario.query.order_by(Scenario.created_at.desc()).all()
    return jsonify([s.to_dict() for s in scenarios])


@bp.route('/<int:id>', methods=['GET'])
def get_scenario(id):
    """Get single scenario"""
    scenario = Scenario.query.get_or_404(id)
    return jsonify(scenario.to_dict())


@bp.route('/', methods=['POST'])
def create_scenario():
    """Create new scenario"""
    data = request.get_json()

    # Validate required fields
    if not data.get('name') or not data.get('parameters'):
        return jsonify({'error': 'Name and parameters are required'}), 400
    
    # Validate parameters
    is_valid, errors = ParameterValidator.validate_parameters(data['parameters'])
    if not is_valid:
        return jsonify({'error': 'Invalid parameters', 'details': errors}), 400

    scenario = Scenario(
        name=data['name'],
        description=data.get('description', ''),
        parameters=data['parameters']
    )

    # Check cache first
    cached_results = CacheService.get_cached_scenario_results(data['parameters'])
    if cached_results:
        scenario.results = cached_results
    else:
        # Run model calculations
        model_service = ModelService()
        try:
            results = model_service.calculate_impacts(data['parameters'])
            scenario.results = results
            # Cache the results
            CacheService.cache_scenario_results(data['parameters'], results)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    db.session.add(scenario)
    db.session.commit()

    return jsonify(scenario.to_dict()), 201


@bp.route('/<int:id>', methods=['PUT'])
def update_scenario(id):
    """Update scenario"""
    scenario = Scenario.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data:
        scenario.name = data['name']
    if 'description' in data:
        scenario.description = data['description']
    if 'parameters' in data:
        # Validate parameters
        is_valid, errors = ParameterValidator.validate_parameters(data['parameters'])
        if not is_valid:
            return jsonify({'error': 'Invalid parameters', 'details': errors}), 400
        
        scenario.parameters = data['parameters']
        
        # Check cache
        cached_results = CacheService.get_cached_scenario_results(data['parameters'])
        if cached_results:
            scenario.results = cached_results
        else:
            # Recalculate results
            model_service = ModelService()
            try:
                results = model_service.calculate_impacts(data['parameters'])
                scenario.results = results
                CacheService.cache_scenario_results(data['parameters'], results)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

    db.session.commit()
    return jsonify(scenario.to_dict())


@bp.route('/<int:id>', methods=['DELETE'])
def delete_scenario(id):
    """Delete scenario"""
    scenario = Scenario.query.get_or_404(id)
    db.session.delete(scenario)
    db.session.commit()
    return '', 204


@bp.route('/compare', methods=['POST'])
def compare_scenarios():
    """Compare multiple scenarios"""
    data = request.get_json()
    scenario_ids = data.get('scenario_ids', [])

    if len(scenario_ids) < 2:
        return jsonify({'error': 'At least 2 scenarios required for comparison'}), 400

    # Check cache
    cached_comparison = CacheService.get_cached_comparison(scenario_ids)
    if cached_comparison:
        return jsonify(cached_comparison)

    scenarios = Scenario.query.filter(Scenario.id.in_(scenario_ids)).all()

    comparison = {
        'scenarios': [s.to_dict() for s in scenarios],
        'metrics': ModelService.compare_metrics([s.results for s in scenarios])
    }
    
    # Cache the comparison
    CacheService.cache_comparison(scenario_ids, comparison)

    return jsonify(comparison)


@bp.route('/<int:id>/sensitivity', methods=['POST'])
def sensitivity_analysis(id):
    """Run sensitivity analysis on a scenario"""
    scenario = Scenario.query.get_or_404(id)
    data = request.get_json() or {}
    parameter_to_vary = data.get('parameter')
    
    # Check cache
    if parameter_to_vary:
        cached = CacheService.get_cached_sensitivity_analysis(id, parameter_to_vary)
        if cached:
            return jsonify(cached)
    
    # Run sensitivity analysis
    model_service = ModelService()
    try:
        results = model_service.sensitivity_analysis(
            scenario.parameters,
            parameter_to_vary=parameter_to_vary
        )
        
        # Cache results
        if parameter_to_vary:
            CacheService.cache_sensitivity_analysis(id, parameter_to_vary, results)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/what-changed', methods=['POST'])
def what_changed():
    """Explain what changed between two scenarios"""
    data = request.get_json()
    scenario1_id = data.get('scenario1_id')
    scenario2_id = data.get('scenario2_id')
    
    if not scenario1_id or not scenario2_id:
        return jsonify({'error': 'Both scenario1_id and scenario2_id are required'}), 400
    
    scenario1 = Scenario.query.get_or_404(scenario1_id)
    scenario2 = Scenario.query.get_or_404(scenario2_id)
    
    explanation = ScenarioExplainer.explain_what_changed(
        scenario1.to_dict(),
        scenario2.to_dict()
    )
    
    return jsonify({
        'scenario1': {
            'id': scenario1.id,
            'name': scenario1.name
        },
        'scenario2': {
            'id': scenario2.id,
            'name': scenario2.name
        },
        'explanation': explanation
    })


@bp.route('/<int:id>/projection', methods=['POST'])
def time_series_projection(id):
    """Get time-series projection for a scenario"""
    scenario = Scenario.query.get_or_404(id)
    data = request.get_json() or {}
    years = data.get('years', 10)
    
    if years < 1 or years > 50:
        return jsonify({'error': 'Years must be between 1 and 50'}), 400
    
    model_service = ModelService()
    try:
        projection = model_service.time_series_projection(scenario.parameters, years=years)
        return jsonify(projection)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:id>/export', methods=['GET'])
def export_scenario(id):
    """Export scenario data"""
    scenario = Scenario.query.get_or_404(id)
    export_format = request.args.get('format', 'json').lower()
    
    scenario_dict = scenario.to_dict()
    
    if export_format == 'csv':
        csv_data = ExportService.export_scenario_to_csv(scenario_dict)
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=scenario_{id}.csv'}
        )
    elif export_format == 'json':
        json_data = ExportService.export_to_json(scenario_dict)
        return Response(
            json_data,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=scenario_{id}.json'}
        )
    elif export_format == 'txt':
        txt_data = ExportService.create_summary_report(scenario_dict)
        return Response(
            txt_data,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename=scenario_{id}.txt'}
        )
    else:
        return jsonify({'error': 'Invalid format. Use csv, json, or txt'}), 400


@bp.route('/compare/export', methods=['POST'])
def export_comparison():
    """Export scenario comparison"""
    data = request.get_json()
    scenario_ids = data.get('scenario_ids', [])
    export_format = data.get('format', 'json').lower()
    
    if len(scenario_ids) < 2:
        return jsonify({'error': 'At least 2 scenarios required'}), 400
    
    scenarios = Scenario.query.filter(Scenario.id.in_(scenario_ids)).all()
    scenario_dicts = [s.to_dict() for s in scenarios]
    
    if export_format == 'csv':
        csv_data = ExportService.export_comparison_to_csv(scenario_dicts)
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=comparison.csv'}
        )
    elif export_format == 'json':
        comparison = {
            'scenarios': scenario_dicts,
            'metrics': ModelService.compare_metrics([s.results for s in scenarios])
        }
        json_data = ExportService.export_to_json(comparison)
        return Response(
            json_data,
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=comparison.json'}
        )
    else:
        return jsonify({'error': 'Invalid format. Use csv or json'}), 400
