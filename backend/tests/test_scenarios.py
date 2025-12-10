import pytest
from backend.app import create_app, db
from backend.models.scenario import Scenario


@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def sample_scenario(app):
    """Create a sample scenario for testing"""
    with app.app_context():
        scenario = Scenario(
            name='Test Scenario',
            description='A test scenario',
            parameters={
                'food_production_intensity': 0.7,
                'renewable_energy_share': 0.6,
                'water_conservation_level': 0.5,
                'population_growth': 1.02
            },
            results={
                'food_production': 1000,
                'co2_emissions': 500,
                'water_demand': 3000,
                'water_stress_index': 0.3,
                'food_security_index': 0.8,
                'sustainability_score': 0.7
            }
        )
        db.session.add(scenario)
        db.session.commit()
        yield scenario


class TestScenarioAPI:
    """Test scenario API endpoints"""
    
    def test_create_scenario(self, client):
        """Test creating a new scenario"""
        response = client.post('/api/scenarios/', json={
            'name': 'New Scenario',
            'description': 'Test description',
            'parameters': {
                'food_production_intensity': 0.8,
                'renewable_energy_share': 0.6,
                'water_conservation_level': 0.5,
                'population_growth': 1.02
            }
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Scenario'
        assert 'results' in data
        assert 'id' in data
    
    def test_create_scenario_validation(self, client):
        """Test parameter validation on create"""
        # Invalid parameter value (out of range)
        response = client.post('/api/scenarios/', json={
            'name': 'Invalid Scenario',
            'parameters': {
                'renewable_energy_share': 1.5  # Invalid: max is 1.0
            }
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_scenario_missing_fields(self, client):
        """Test creating scenario with missing required fields"""
        response = client.post('/api/scenarios/', json={
            'name': 'No Parameters'
        })
        
        assert response.status_code == 400
    
    def test_get_all_scenarios(self, client, sample_scenario):
        """Test getting all scenarios"""
        response = client.get('/api/scenarios/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_single_scenario(self, client, sample_scenario):
        """Test getting a single scenario"""
        response = client.get(f'/api/scenarios/{sample_scenario.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == sample_scenario.id
        assert data['name'] == sample_scenario.name
    
    def test_get_nonexistent_scenario(self, client):
        """Test getting a scenario that doesn't exist"""
        response = client.get('/api/scenarios/9999')
        
        assert response.status_code == 404
    
    def test_update_scenario(self, client, sample_scenario):
        """Test updating a scenario"""
        response = client.put(f'/api/scenarios/{sample_scenario.id}', json={
            'name': 'Updated Name',
            'description': 'Updated description'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Name'
        assert data['description'] == 'Updated description'
    
    def test_update_scenario_parameters(self, client, sample_scenario):
        """Test updating scenario parameters (triggers recalculation)"""
        response = client.put(f'/api/scenarios/{sample_scenario.id}', json={
            'parameters': {
                'food_production_intensity': 0.9,
                'renewable_energy_share': 0.8,
                'water_conservation_level': 0.6,
                'population_growth': 1.01
            }
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['parameters']['food_production_intensity'] == 0.9
        # Results should be recalculated
        assert 'results' in data
    
    def test_delete_scenario(self, client, sample_scenario):
        """Test deleting a scenario"""
        scenario_id = sample_scenario.id
        response = client.delete(f'/api/scenarios/{scenario_id}')
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f'/api/scenarios/{scenario_id}')
        assert response.status_code == 404
    
    def test_compare_scenarios(self, client, app):
        """Test scenario comparison"""
        # Create two scenarios
        with app.app_context():
            scenario1 = Scenario(
                name='Scenario 1',
                parameters={'renewable_energy_share': 0.3},
                results={'co2_emissions': 600, 'water_demand': 3500}
            )
            scenario2 = Scenario(
                name='Scenario 2',
                parameters={'renewable_energy_share': 0.8},
                results={'co2_emissions': 400, 'water_demand': 3000}
            )
            db.session.add_all([scenario1, scenario2])
            db.session.commit()
            
            ids = [scenario1.id, scenario2.id]
        
        response = client.post('/api/scenarios/compare', json={
            'scenario_ids': ids
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'scenarios' in data
        assert 'metrics' in data
        assert len(data['scenarios']) == 2
    
    def test_compare_insufficient_scenarios(self, client):
        """Test comparison with insufficient scenarios"""
        response = client.post('/api/scenarios/compare', json={
            'scenario_ids': [1]
        })
        
        assert response.status_code == 400
    
    def test_sensitivity_analysis(self, client, sample_scenario):
        """Test sensitivity analysis endpoint"""
        response = client.post(f'/api/scenarios/{sample_scenario.id}/sensitivity', json={
            'parameter': 'renewable_energy_share'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'baseline' in data
        assert 'analysis' in data
        assert 'renewable_energy_share' in data['analysis']
    
    def test_what_changed(self, client, app):
        """Test what-changed endpoint"""
        # Create two scenarios
        with app.app_context():
            scenario1 = Scenario(
                name='Before',
                parameters={'renewable_energy_share': 0.3, 'food_production_intensity': 0.5},
                results={'co2_emissions': 600, 'water_demand': 3500}
            )
            scenario2 = Scenario(
                name='After',
                parameters={'renewable_energy_share': 0.8, 'food_production_intensity': 0.5},
                results={'co2_emissions': 400, 'water_demand': 3000}
            )
            db.session.add_all([scenario1, scenario2])
            db.session.commit()
            
            ids = (scenario1.id, scenario2.id)
        
        response = client.post('/api/scenarios/what-changed', json={
            'scenario1_id': ids[0],
            'scenario2_id': ids[1]
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'explanation' in data
        assert 'parameter_changes' in data['explanation']
        assert 'outcome_changes' in data['explanation']
    
    def test_time_series_projection(self, client, sample_scenario):
        """Test time-series projection endpoint"""
        response = client.post(f'/api/scenarios/{sample_scenario.id}/projection', json={
            'years': 5
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'projections' in data
        assert len(data['projections']) == 6  # 0-5 years
    
    def test_export_scenario_json(self, client, sample_scenario):
        """Test exporting scenario as JSON"""
        response = client.get(f'/api/scenarios/{sample_scenario.id}/export?format=json')
        
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
    
    def test_export_scenario_csv(self, client, sample_scenario):
        """Test exporting scenario as CSV"""
        response = client.get(f'/api/scenarios/{sample_scenario.id}/export?format=csv')
        
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert 'scenario_' in response.headers['Content-Disposition']
    
    def test_export_scenario_txt(self, client, sample_scenario):
        """Test exporting scenario as text summary"""
        response = client.get(f'/api/scenarios/{sample_scenario.id}/export?format=txt')
        
        assert response.status_code == 200
        assert response.mimetype == 'text/plain'