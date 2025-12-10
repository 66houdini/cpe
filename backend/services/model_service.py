import numpy as np
from typing import Dict, List
from backend.utils.validators import ParameterValidator


class ModelService:
    """
    Handles food-energy-water nexus calculations
    Enhanced with sensitivity analysis, time-series, and feedback loops
    """

    def calculate_impacts(self, parameters: Dict, use_cache: bool = True) -> Dict:
        """
        Calculate nexus impacts based on policy parameters
        
        Parameters example:
        {
            "food_production_intensity": 0.8,  # 0-1 scale
            "renewable_energy_share": 0.6,
            "water_conservation_level": 0.7,
            "population_growth": 1.02  # annual rate
        }
        """
        # Fill in defaults for missing parameters
        params = ParameterValidator.fill_defaults(parameters)
        
        # Validate parameters
        is_valid, errors = ParameterValidator.validate_parameters(params)
        if not is_valid:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")
        
        # Extract parameters
        food_intensity = params['food_production_intensity']
        renewable_share = params['renewable_energy_share']
        water_conservation = params['water_conservation_level']
        pop_growth = params['population_growth']

        # Base values
        base_food_production = 1000
        base_energy = 5000
        base_water_available = 10000

        # Food sector calculations with feedback loops
        food_production = base_food_production * food_intensity * pop_growth
        
        # Water demand for food (reduced by conservation measures)
        food_water_demand = food_production * 2.5 * (1 - water_conservation * 0.3)
        
        # Energy demand for food production
        food_energy_demand = food_production * 0.8

        # Energy sector calculations
        total_energy = base_energy * pop_growth
        renewable_energy = total_energy * renewable_share
        fossil_energy = total_energy * (1 - renewable_share)
        
        # CO2 emissions (fossil fuels emit, renewables don't)
        co2_emissions = fossil_energy * 0.5
        
        # Water demand for energy (fossil is water-intensive, renewables less so)
        energy_water_demand = fossil_energy * 1.2 + renewable_energy * 0.3

        # Water sector calculations
        domestic_water_demand = 1500 * pop_growth
        total_water_demand = food_water_demand + energy_water_demand + domestic_water_demand
        
        # Water conservation reduces demand
        total_water_demand *= (1 - water_conservation * 0.15)
        
        # Water stress (0-1 scale)
        water_stress_index = min(total_water_demand / base_water_available, 1.0)
        
        # Feedback: water stress affects food production
        water_stress_penalty = 1 - (water_stress_index * 0.2)  # Up to 20% penalty
        adjusted_food_production = food_production * water_stress_penalty
        
        # Food security index (can we meet demand?)
        food_security_index = min(adjusted_food_production / (base_food_production * pop_growth), 1.0)
        
        # Energy security index
        energy_security_index = min(total_energy / (base_energy * pop_growth), 1.0)
        
        # Calculate uncertainties
        uncertainties = self._calculate_uncertainties(params)

        return {
            'food_production': round(adjusted_food_production, 2),
            'food_water_demand': round(food_water_demand, 2),
            'food_energy_demand': round(food_energy_demand, 2),
            'total_energy': round(total_energy, 2),
            'renewable_energy': round(renewable_energy, 2),
            'fossil_energy': round(fossil_energy, 2),
            'co2_emissions': round(co2_emissions, 2),
            'water_demand': round(total_water_demand, 2),
            'water_stress_index': round(water_stress_index, 3),
            'food_security_index': round(food_security_index, 3),
            'energy_security_index': round(energy_security_index, 3),
            'sustainability_score': round(self._calculate_sustainability_score({
                'co2_emissions': co2_emissions,
                'water_stress_index': water_stress_index,
                'food_security_index': food_security_index,
                'renewable_share': renewable_share
            }), 3),
            'uncertainties': uncertainties
        }

    def _calculate_uncertainties(self, parameters: Dict) -> Dict:
        """Calculate uncertainty bands using Monte Carlo simulation"""
        from flask import current_app
        
        try:
            n_simulations = current_app.config.get('MC_SIMULATIONS', 100)
        except RuntimeError:
            # Handle case when called outside app context
            n_simulations = 100

        results_list = []
        
        # Run Monte Carlo simulations with parameter uncertainty
        for _ in range(n_simulations):
            # Add random variation to parameters (±10% standard deviation)
            varied_params = {}
            for k, v in parameters.items():
                # Add noise but keep within valid ranges
                noise = np.random.normal(0, 0.1)
                varied_value = v * (1 + noise)
                
                # Clamp to valid ranges
                constraints = ParameterValidator.PARAMETER_CONSTRAINTS.get(k, {})
                min_val = constraints.get('min', 0)
                max_val = constraints.get('max', 10)
                varied_params[k] = max(min_val, min(max_val, varied_value))
            
            # Don't recurse into uncertainty calculation
            try:
                result = self._calculate_base_impacts(varied_params)
                results_list.append(result)
            except:
                continue

        if not results_list:
            return {}

        # Calculate percentiles
        metrics = ['co2_emissions', 'water_demand', 'food_production', 'water_stress_index']
        uncertainties = {}

        for metric in metrics:
            values = [r.get(metric, 0) for r in results_list if metric in r]
            if values:
                uncertainties[metric] = {
                    'p10': round(float(np.percentile(values, 10)), 2),
                    'p50': round(float(np.percentile(values, 50)), 2),
                    'p90': round(float(np.percentile(values, 90)), 2)
                }

        return uncertainties

    def _calculate_base_impacts(self, parameters: Dict) -> Dict:
        """Calculate impacts without uncertainty quantification (for MC simulation)"""
        params = ParameterValidator.fill_defaults(parameters)
        
        food_intensity = params['food_production_intensity']
        renewable_share = params['renewable_energy_share']
        water_conservation = params['water_conservation_level']
        pop_growth = params['population_growth']

        base_food_production = 1000
        base_energy = 5000
        base_water_available = 10000

        food_production = base_food_production * food_intensity * pop_growth
        food_water_demand = food_production * 2.5 * (1 - water_conservation * 0.3)
        total_energy = base_energy * pop_growth
        renewable_energy = total_energy * renewable_share
        fossil_energy = total_energy * (1 - renewable_share)
        co2_emissions = fossil_energy * 0.5
        energy_water_demand = fossil_energy * 1.2 + renewable_energy * 0.3
        domestic_water_demand = 1500 * pop_growth
        total_water_demand = (food_water_demand + energy_water_demand + domestic_water_demand) * (1 - water_conservation * 0.15)
        water_stress_index = min(total_water_demand / base_water_available, 1.0)
        
        water_stress_penalty = 1 - (water_stress_index * 0.2)
        adjusted_food_production = food_production * water_stress_penalty

        return {
            'food_production': adjusted_food_production,
            'co2_emissions': co2_emissions,
            'water_demand': total_water_demand,
            'water_stress_index': water_stress_index
        }

    def _calculate_sustainability_score(self, metrics: Dict) -> float:
        """
        Calculate overall sustainability score (0-1, higher is better)
        Weighted combination of key metrics
        """
        # Normalize CO2 (lower is better)
        co2_score = max(0, 1 - (metrics['co2_emissions'] / 3000))  # 3000 is high emissions
        
        # Water stress (lower is better)
        water_score = 1 - metrics['water_stress_index']
        
        # Food security (higher is better)
        food_score = metrics['food_security_index']
        
        # Renewable share (higher is better)
        renewable_score = metrics['renewable_share']
        
        # Weighted average
        score = (co2_score * 0.3 + water_score * 0.3 + food_score * 0.2 + renewable_score * 0.2)
        return max(0, min(1, score))

    def sensitivity_analysis(self, base_parameters: Dict, parameter_to_vary: str = None) -> Dict:
        """
        Perform one-at-a-time sensitivity analysis
        
        Args:
            base_parameters: Baseline scenario parameters
            parameter_to_vary: Specific parameter to analyze, or None for all
            
        Returns:
            Sensitivity results with variation data
        """
        params = ParameterValidator.fill_defaults(base_parameters)
        
        # Get baseline results
        baseline_results = self.calculate_impacts(params, use_cache=False)
        
        # Determine which parameters to analyze
        if parameter_to_vary:
            params_to_analyze = [parameter_to_vary]
        else:
            params_to_analyze = list(ParameterValidator.PARAMETER_CONSTRAINTS.keys())
        
        sensitivity_results = {
            'baseline': {
                'parameters': params,
                'results': baseline_results
            },
            'analysis': {}
        }
        
        # Vary each parameter
        for param_name in params_to_analyze:
            if param_name not in params:
                continue
            
            constraints = ParameterValidator.PARAMETER_CONSTRAINTS[param_name]
            min_val = constraints['min']
            max_val = constraints['max']
            
            # Create variation points (10 steps across range)
            variation_points = np.linspace(min_val, max_val, 10)
            
            variations = []
            for value in variation_points:
                varied_params = params.copy()
                varied_params[param_name] = float(value)
                
                try:
                    results = self.calculate_impacts(varied_params, use_cache=False)
                    variations.append({
                        'parameter_value': round(float(value), 3),
                        'results': results
                    })
                except:
                    continue
            
            # Calculate sensitivity metrics
            sensitivity_results['analysis'][param_name] = {
                'variations': variations,
                'sensitivity_scores': self._calculate_sensitivity_scores(variations, baseline_results)
            }
        
        return sensitivity_results

    def _calculate_sensitivity_scores(self, variations: List[Dict], baseline: Dict) -> Dict:
        """Calculate how sensitive each outcome is to parameter changes"""
        if not variations or len(variations) < 2:
            return {}
        
        metrics = ['co2_emissions', 'water_demand', 'food_production', 'water_stress_index']
        scores = {}
        
        for metric in metrics:
            values = [v['results'].get(metric, 0) for v in variations]
            baseline_val = baseline.get(metric, 0)
            
            if baseline_val == 0:
                continue
            
            # Calculate coefficient of variation
            std_dev = float(np.std(values))
            mean_val = float(np.mean(values))
            
            # Sensitivity score: how much does output vary relative to baseline?
            if mean_val != 0:
                sensitivity = std_dev / abs(mean_val)
            else:
                sensitivity = 0
            
            scores[metric] = {
                'sensitivity': round(sensitivity, 3),
                'min': round(float(np.min(values)), 2),
                'max': round(float(np.max(values)), 2),
                'range': round(float(np.max(values) - np.min(values)), 2)
            }
        
        return scores

    def time_series_projection(self, parameters: Dict, years: int = 10) -> Dict:
        """
        Project impacts over multiple years
        
        Args:
            parameters: Initial parameters
            years: Number of years to project
            
        Returns:
            Year-by-year projections
        """
        params = ParameterValidator.fill_defaults(parameters)
        pop_growth = params['population_growth']
        
        projections = []
        
        for year in range(years + 1):
            # Adjust for cumulative population growth
            year_params = params.copy()
            year_params['population_growth'] = pop_growth ** year
            
            results = self.calculate_impacts(year_params, use_cache=False)
            projections.append({
                'year': year,
                'results': results
            })
        
        return {
            'projections': projections,
            'parameters': parameters,
            'years': years
        }

    @staticmethod
    def compare_metrics(results_list: List[Dict]) -> Dict:
        """Compare metrics across scenarios"""
        metrics = ['co2_emissions', 'water_demand', 'food_production', 
                  'water_stress_index', 'food_security_index', 'sustainability_score']

        comparison = {}
        for metric in metrics:
            values = [r.get(metric, 0) for r in results_list]
            if values:
                comparison[metric] = {
                    'min': round(float(np.min(values)), 2),
                    'max': round(float(np.max(values)), 2),
                    'mean': round(float(np.mean(values)), 2),
                    'values': [round(float(v), 2) for v in values]
                }

        return comparison
