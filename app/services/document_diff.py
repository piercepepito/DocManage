import difflib

from uuid import UUID

from app.databases import models

import logging
logger = logging.getLogger(__name__)

def compare_docs(
    old_document: models.Documents,
    new_document: models.Documents,
) -> str:
    """
    Gets the difference between both documents (any new lines, deleted, and modified)

    Args:
        old_document: the reference document that is compared from
        new_document: the newest version that should be compared to
    Returns:
        str: gets the difference (modification, deletes, and additions) of both files
    """
    logger.info(f"Getting the difference between 2 documents of document_id: {new_document.id}")

    old_content = old_document.content
    old_version = old_document.version

    new_content = new_document.content
    new_version = new_document.version

    diff = difflib.unified_diff(
        a=old_content.splitlines(keepends=True),
        b=new_content.splitlines(keepends=True),
        fromfile="version "  + f"{str(old_version)}",
        tofile="version " + f"{str(new_version)}",
        n=3
    )

    logger.info("Succesfully found the difference between both document files")
    return "".join(diff)