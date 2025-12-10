import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Caching configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour default
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Model configuration
    MODEL_CACHE_TIMEOUT = 3600  # Cache model results for 1 hour
    SENSITIVITY_CACHE_TIMEOUT = 7200  # Cache sensitivity analysis for 2 hours
    COMPARISON_CACHE_TIMEOUT = 1800  # Cache comparisons for 30 minutes
    
    # Monte Carlo simulation settings
    MC_SIMULATIONS = int(os.environ.get('MC_SIMULATIONS', '100'))
    MC_CONFIDENCE_LEVELS = [10, 50, 90]  # Percentiles for uncertainty bands


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'data-dev.sqlite')
    CACHE_TYPE = 'simple'  # In-memory cache for development


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_TYPE = 'simple'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/nexus_platform'
    
    # Use Redis for production caching
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'nexus_'
    
    # Stricter settings for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
