class AutoTestProException(Exception):
    """Base exception for AutoTest Pro Framework."""


class BrowserNotSupportedError(AutoTestProException):
    """Raised when an unsupported browser is requested."""


class ElementActionError(AutoTestProException):
    """Raised when an element action fails."""


class ConfigurationError(AutoTestProException):
    """Raised when configuration is invalid."""
