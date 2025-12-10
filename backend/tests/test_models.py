import pytest
from backend.app import create_app, db
from backend.models.scenario import Scenario, ModelAssumption
from backend.services.model_service import ModelService


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


@pytest.fixture
def sample_parameters():
    """Sample valid parameters"""
    return {
        'food_production_intensity': 0.7,
        'renewable_energy_share': 0.6,
        'water_conservation_level': 0.5,
        'population_growth': 1.02
    }


class TestModelService:
    """Test model calculations"""
    
    def test_calculate_impacts_basic(self, app, sample_parameters):
        """Test basic impact calculation"""
        with app.app_context():
            model_service = ModelService()
            results = model_service.calculate_impacts(sample_parameters)
            
            # Check that all expected keys are present
            assert 'food_production' in results
            assert 'co2_emissions' in results
            assert 'water_demand' in results
            assert 'water_stress_index' in results
            assert 'food_security_index' in results
            assert 'sustainability_score' in results
            
            # Check value ranges
            assert results['water_stress_index'] >= 0
            assert results['water_stress_index'] <= 1
            assert results['food_security_index'] >= 0
            assert results['food_security_index'] <= 1
            assert results['sustainability_score'] >= 0
            assert results['sustainability_score'] <= 1
    
    def test_calculate_impacts_with_defaults(self, app):
        """Test calculation with missing parameters (should use defaults)"""
        with app.app_context():
            model_service = ModelService()
            results = model_service.calculate_impacts({})
            
            assert 'food_production' in results
            assert results['food_production'] > 0
    
    def test_invalid_parameters(self, app):
        """Test validation of invalid parameters"""
        with app.app_context():
            model_service = ModelService()
            
            # Out of range
            with pytest.raises(ValueError):
                model_service.calculate_impacts({
                    'renewable_energy_share': 1.5  # Max is 1.0
                })
    
    def test_sensitivity_analysis(self, app, sample_parameters):
        """Test sensitivity analysis"""
        with app.app_context():
            model_service = ModelService()
            results = model_service.sensitivity_analysis(
                sample_parameters,
                parameter_to_vary='renewable_energy_share'
            )
            
            assert 'baseline' in results
            assert 'analysis' in results
            assert 'renewable_energy_share' in results['analysis']
            
            variations = results['analysis']['renewable_energy_share']['variations']
            assert len(variations) > 0
            assert 'parameter_value' in variations[0]
            assert 'results' in variations[0]
    
    def test_time_series_projection(self, app, sample_parameters):
        """Test time series projection"""
        with app.app_context():
            model_service = ModelService()
            results = model_service.time_series_projection(sample_parameters, years=5)
            
            assert 'projections' in results
            assert len(results['projections']) == 6  # 0-5 years
            assert 'year' in results['projections'][0]
            assert 'results' in results['projections'][0]
    
    def test_compare_metrics(self, app):
        """Test metric comparison"""
        results_list = [
            {'co2_emissions': 500, 'water_demand': 3000},
            {'co2_emissions': 600, 'water_demand': 3500},
            {'co2_emissions': 450, 'water_demand': 2800}
        ]
        
        comparison = ModelService.compare_metrics(results_list)
        
        assert 'co2_emissions' in comparison
        assert comparison['co2_emissions']['min'] == 450
        assert comparison['co2_emissions']['max'] == 600
        assert 'mean' in comparison['co2_emissions']
