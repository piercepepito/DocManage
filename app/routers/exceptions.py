class DatabaseStorageError(Exception):
    """
    Raises when the document doesn't save due to a system error
    """
    pass

class NoDocumentFound(Exception):
    """
    Raises when it cannot find the document
    """
    pass

class DocumentConflictError(Exception):
    """
    Raises when concurrency issue occurs wherein both users have the same version when opened
    """
    pass