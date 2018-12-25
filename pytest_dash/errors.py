class PytestDashError(Exception):
    pass


class NoAppFoundError(PytestDashError):
    """No `app` was found in the file."""


class DashAppLoadingError(PytestDashError):
    """The dash app failed to load"""
