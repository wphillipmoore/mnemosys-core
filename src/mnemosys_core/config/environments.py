"""
Environment types for configuration.
"""

import enum


class Environment(enum.Enum):
    """Deployment environment identifiers."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"
