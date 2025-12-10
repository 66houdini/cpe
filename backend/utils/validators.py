from typing import Dict, List, Tuple


class ParameterValidator:
    """Validates scenario parameters"""
    
    # Define parameter constraints
    PARAMETER_CONSTRAINTS = {
        'food_production_intensity': {
            'min': 0.0,
            'max': 1.0,
            'type': float,
            'required': False,
            'default': 0.5
        },
        'renewable_energy_share': {
            'min': 0.0,
            'max': 1.0,
            'type': float,
            'required': False,
            'default': 0.3
        },
        'water_conservation_level': {
            'min': 0.0,
            'max': 1.0,
            'type': float,
            'required': False,
            'default': 0.5
        },
        'population_growth': {
            'min': 0.95,
            'max': 1.10,
            'type': float,
            'required': False,
            'default': 1.01
        }
    }
    
    @staticmethod
    def validate_parameters(parameters: Dict) -> Tuple[bool, List[str]]:
        """
        Validate scenario parameters
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not isinstance(parameters, dict):
            return False, ["Parameters must be a dictionary"]
        
        # Check each provided parameter
        for param_name, param_value in parameters.items():
            if param_name not in ParameterValidator.PARAMETER_CONSTRAINTS:
                errors.append(f"Unknown parameter: {param_name}")
                continue
            
            constraints = ParameterValidator.PARAMETER_CONSTRAINTS[param_name]
            
            # Type check
            if not isinstance(param_value, (int, float)):
                errors.append(f"{param_name} must be a number, got {type(param_value).__name__}")
                continue
            
            # Range check
            if param_value < constraints['min'] or param_value > constraints['max']:
                errors.append(
                    f"{param_name} must be between {constraints['min']} and {constraints['max']}, "
                    f"got {param_value}"
                )
        
        # Check required parameters
        for param_name, constraints in ParameterValidator.PARAMETER_CONSTRAINTS.items():
            if constraints.get('required') and param_name not in parameters:
                errors.append(f"Required parameter missing: {param_name}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def fill_defaults(parameters: Dict) -> Dict:
        """Fill in default values for missing parameters"""
        filled_params = parameters.copy()
        
        for param_name, constraints in ParameterValidator.PARAMETER_CONSTRAINTS.items():
            if param_name not in filled_params:
                filled_params[param_name] = constraints['default']
        
        return filled_params
    
    @staticmethod
    def get_parameter_info(parameter_name: str) -> Dict:
        """Get metadata about a specific parameter"""
        if parameter_name not in ParameterValidator.PARAMETER_CONSTRAINTS:
            return None
        
        return ParameterValidator.PARAMETER_CONSTRAINTS[parameter_name]
    
    @staticmethod
    def get_all_parameters() -> Dict:
        """Get all parameter constraints"""
        return ParameterValidator.PARAMETER_CONSTRAINTS.copy()
