"""
Environment types for configuration.
"""

import enum


class Environment(enum.Enum):
    """Deployment environment identifiers."""

    SANDBOX = "sandbox"
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"
