class NotFoundError(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail


class ForbiddenError(Exception):
    def __init__(self, detail: str = "You do not have permission to modify this resource"):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Resource already exists"):
        self.detail = detail
