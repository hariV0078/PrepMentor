class BackendError(Exception):
    pass


class ProviderUnavailableError(BackendError):
    pass


class ProcessingError(BackendError):
    pass
