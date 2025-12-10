import hashlib
import json
from typing import Dict, Any, Optional
from functools import wraps
from flask import current_app
from backend.app import cache


class CacheService:
    """Service for caching expensive model calculations"""
    
    @staticmethod
    def generate_cache_key(prefix: str, data: Dict) -> str:
        """
        Generate a deterministic cache key from a dictionary
        
        Args:
            prefix: Key prefix (e.g., 'scenario', 'sensitivity')
            data: Dictionary to hash
            
        Returns:
            Cache key string
        """
        # Sort dict to ensure consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(sorted_data.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    @staticmethod
    def cache_scenario_results(parameters: Dict, results: Dict) -> None:
        """Cache scenario calculation results"""
        cache_key = CacheService.generate_cache_key('scenario_results', parameters)
        timeout = current_app.config.get('MODEL_CACHE_TIMEOUT', 3600)
        cache.set(cache_key, results, timeout=timeout)
    
    @staticmethod
    def get_cached_scenario_results(parameters: Dict) -> Optional[Dict]:
        """Retrieve cached scenario results"""
        cache_key = CacheService.generate_cache_key('scenario_results', parameters)
        return cache.get(cache_key)
    
    @staticmethod
    def cache_sensitivity_analysis(scenario_id: int, parameter_name: str, results: Dict) -> None:
        """Cache sensitivity analysis results"""
        cache_key = f"sensitivity:{scenario_id}:{parameter_name}"
        timeout = current_app.config.get('SENSITIVITY_CACHE_TIMEOUT', 7200)
        cache.set(cache_key, results, timeout=timeout)
    
    @staticmethod
    def get_cached_sensitivity_analysis(scenario_id: int, parameter_name: str) -> Optional[Dict]:
        """Retrieve cached sensitivity analysis"""
        cache_key = f"sensitivity:{scenario_id}:{parameter_name}"
        return cache.get(cache_key)
    
    @staticmethod
    def cache_comparison(scenario_ids: list, results: Dict) -> None:
        """Cache scenario comparison results"""
        sorted_ids = sorted(scenario_ids)
        cache_key = f"comparison:{'-'.join(map(str, sorted_ids))}"
        timeout = current_app.config.get('COMPARISON_CACHE_TIMEOUT', 1800)
        cache.set(cache_key, results, timeout=timeout)
    
    @staticmethod
    def get_cached_comparison(scenario_ids: list) -> Optional[Dict]:
        """Retrieve cached comparison results"""
        sorted_ids = sorted(scenario_ids)
        cache_key = f"comparison:{'-'.join(map(str, sorted_ids))}"
        return cache.get(cache_key)
    
    @staticmethod
    def invalidate_scenario_cache(parameters: Dict) -> None:
        """Invalidate cache for specific scenario parameters"""
        cache_key = CacheService.generate_cache_key('scenario_results', parameters)
        cache.delete(cache_key)
    
    @staticmethod
    def clear_all_cache() -> None:
        """Clear all cached data (use with caution)"""
        cache.clear()


def cached_model_calculation(timeout: int = 3600):
    """
    Decorator for caching model calculations
    
    Usage:
        @cached_model_calculation(timeout=7200)
        def expensive_calculation(parameters):
            # ... calculation logic
            return results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_data = {
                'args': args,
                'kwargs': kwargs
            }
            cache_key = CacheService.generate_cache_key(func.__name__, cache_data)
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Calculate and cache
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            return result
        
        return wrapper
    return decorator
