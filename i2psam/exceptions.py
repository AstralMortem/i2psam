class SAMError(RuntimeError):
    pass


class SAMClientError(SAMError):
    pass


class SAMClientNotConnected(SAMClientError):
    pass


class SAMSessionError(SAMError):
    pass


class SAMStreamError(SAMError):
    pass


class SAMDatagramError(SAMError):
    pass
