from typing import Dict, List


class ScenarioExplainer:
    """Generates human-readable explanations of scenario changes and impacts"""
    
    # Thresholds for significance
    SIGNIFICANT_CHANGE_THRESHOLD = 0.1  # 10% change is significant
    MAJOR_CHANGE_THRESHOLD = 0.3  # 30% change is major
    
    @staticmethod
    def explain_what_changed(scenario1: Dict, scenario2: Dict) -> Dict:
        """
        Compare two scenarios and explain what changed
        
        Args:
            scenario1: First scenario dict with 'parameters' and 'results'
            scenario2: Second scenario dict with 'parameters' and 'results'
            
        Returns:
            Dictionary with explanations and comparisons
        """
        params1 = scenario1.get('parameters', {})
        params2 = scenario2.get('parameters', {})
        results1 = scenario1.get('results', {})
        results2 = scenario2.get('results', {})
        
        explanation = {
            'parameter_changes': ScenarioExplainer._compare_parameters(params1, params2),
            'outcome_changes': ScenarioExplainer._compare_outcomes(results1, results2),
            'key_insights': ScenarioExplainer._generate_insights(params1, params2, results1, results2),
            'trade_offs': ScenarioExplainer._identify_trade_offs(results1, results2)
        }
        
        return explanation
    
    @staticmethod
    def _compare_parameters(params1: Dict, params2: Dict) -> List[Dict]:
        """Compare parameter changes between scenarios"""
        changes = []
        
        all_params = set(params1.keys()) | set(params2.keys())
        
        for param in all_params:
            val1 = params1.get(param, 0)
            val2 = params2.get(param, 0)
            
            if val1 == val2:
                continue
            
            change = val2 - val1
            pct_change = (change / val1 * 100) if val1 != 0 else 0
            
            # Determine magnitude
            if abs(pct_change) > ScenarioExplainer.MAJOR_CHANGE_THRESHOLD * 100:
                magnitude = 'major'
            elif abs(pct_change) > ScenarioExplainer.SIGNIFICANT_CHANGE_THRESHOLD * 100:
                magnitude = 'significant'
            else:
                magnitude = 'minor'
            
            # Generate human-readable description
            direction = 'increased' if change > 0 else 'decreased'
            param_readable = param.replace('_', ' ').title()
            
            changes.append({
                'parameter': param,
                'parameter_name': param_readable,
                'old_value': round(val1, 3),
                'new_value': round(val2, 3),
                'change': round(change, 3),
                'percent_change': round(pct_change, 1),
                'magnitude': magnitude,
                'description': f"{param_readable} {direction} by {abs(round(pct_change, 1))}%"
            })
        
        return sorted(changes, key=lambda x: abs(x['percent_change']), reverse=True)
    
    @staticmethod
    def _compare_outcomes(results1: Dict, results2: Dict) -> List[Dict]:
        """Compare outcome changes between scenarios"""
        changes = []
        
        # Metrics to compare
        metrics = ['co2_emissions', 'water_demand', 'food_production', 
                  'water_stress_index', 'food_security_index']
        
        for metric in metrics:
            val1 = results1.get(metric, 0)
            val2 = results2.get(metric, 0)
            
            if val1 == val2:
                continue
            
            change = val2 - val1
            pct_change = (change / val1 * 100) if val1 != 0 else 0
            
            # Determine if change is positive or negative for sustainability
            is_improvement = ScenarioExplainer._is_improvement(metric, change)
            
            metric_readable = metric.replace('_', ' ').title()
            direction = 'increased' if change > 0 else 'decreased'
            
            changes.append({
                'metric': metric,
                'metric_name': metric_readable,
                'old_value': round(val1, 2),
                'new_value': round(val2, 2),
                'change': round(change, 2),
                'percent_change': round(pct_change, 1),
                'is_improvement': is_improvement,
                'description': f"{metric_readable} {direction} by {abs(round(pct_change, 1))}%"
            })
        
        return sorted(changes, key=lambda x: abs(x['percent_change']), reverse=True)
    
    @staticmethod
    def _is_improvement(metric: str, change: float) -> bool:
        """Determine if a change is an improvement for sustainability"""
        # Metrics where decrease is better
        decrease_is_better = ['co2_emissions', 'water_demand', 'water_stress_index']
        # Metrics where increase is better
        increase_is_better = ['food_production', 'food_security_index', 'renewable_energy']
        
        if metric in decrease_is_better:
            return change < 0
        elif metric in increase_is_better:
            return change > 0
        else:
            return False
    
    @staticmethod
    def _generate_insights(params1: Dict, params2: Dict, results1: Dict, results2: Dict) -> List[str]:
        """Generate key insights from the comparison"""
        insights = []
        
        # Check for major policy shifts
        renewable_change = params2.get('renewable_energy_share', 0) - params1.get('renewable_energy_share', 0)
        if renewable_change > 0.2:
            co2_change_pct = ((results2.get('co2_emissions', 0) - results1.get('co2_emissions', 0)) / 
                             results1.get('co2_emissions', 1)) * 100
            insights.append(
                f"Increasing renewable energy share by {renewable_change*100:.0f}% "
                f"reduced CO2 emissions by {abs(co2_change_pct):.1f}%"
            )
        
        # Check for water-food trade-offs
        water_cons_change = params2.get('water_conservation_level', 0) - params1.get('water_conservation_level', 0)
        if abs(water_cons_change) > 0.1:
            water_demand_change_pct = ((results2.get('water_demand', 0) - results1.get('water_demand', 0)) / 
                                       results1.get('water_demand', 1)) * 100
            insights.append(
                f"Water conservation measures led to {abs(water_demand_change_pct):.1f}% "
                f"{'reduction' if water_demand_change_pct < 0 else 'increase'} in water demand"
            )
        
        # Overall sustainability assessment
        improvements = sum([
            results2.get('co2_emissions', 0) < results1.get('co2_emissions', 0),
            results2.get('water_stress_index', 0) < results1.get('water_stress_index', 0),
            results2.get('food_security_index', 0) > results1.get('food_security_index', 0)
        ])
        
        if improvements >= 2:
            insights.append("This scenario shows net positive outcomes across multiple sustainability metrics")
        elif improvements == 0:
            insights.append("This scenario may require optimization to improve sustainability outcomes")
        
        return insights
    
    @staticmethod
    def _identify_trade_offs(results1: Dict, results2: Dict) -> List[Dict]:
        """Identify trade-offs where one metric improves but another worsens"""
        trade_offs = []
        
        metrics = {
            'co2_emissions': 'decrease',
            'water_demand': 'decrease',
            'water_stress_index': 'decrease',
            'food_production': 'increase',
            'food_security_index': 'increase'
        }
        
        changes = {}
        for metric, desired_direction in metrics.items():
            val1 = results1.get(metric, 0)
            val2 = results2.get(metric, 0)
            change = val2 - val1
            
            is_improvement = (change < 0 and desired_direction == 'decrease') or \
                           (change > 0 and desired_direction == 'increase')
            
            changes[metric] = {
                'change': change,
                'is_improvement': is_improvement,
                'pct_change': (change / val1 * 100) if val1 != 0 else 0
            }
        
        # Identify significant trade-offs
        for metric1 in metrics:
            for metric2 in metrics:
                if metric1 >= metric2:
                    continue
                
                if (changes[metric1]['is_improvement'] and not changes[metric2]['is_improvement'] and
                    abs(changes[metric1]['pct_change']) > 5 and abs(changes[metric2]['pct_change']) > 5):
                    
                    trade_offs.append({
                        'improved': metric1.replace('_', ' ').title(),
                        'worsened': metric2.replace('_', ' ').title(),
                        'description': f"Improving {metric1.replace('_', ' ')} came at the cost of {metric2.replace('_', ' ')}"
                    })
        
        return trade_offs
