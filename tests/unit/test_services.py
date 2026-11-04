import pytest
from unittest.mock import patch, Mock

from app.services import document_diff
'''
2. Added something
3. Deleted something
4. modified content
5. Similar document
'''

class TestCompareDocs:
    def test_similar_docs(self):
        mock_old_doc = Mock()
        mock_old_doc.content = """1 cup of mayonnaise\n"""
        mock_old_doc.version = 2

        mock_new_doc = Mock()
        mock_new_doc.content = """1 cup of mayonnaise\n"""
        mock_new_doc.version = 3 

        response = document_diff.compare_docs(old_document=mock_old_doc,
                                              new_document=mock_new_doc)

        expected_response = ""

        assert response == expected_response

    def test_deleted_line(self):
        mock_old_doc = Mock()
        mock_old_doc.content = """1 cup of mayonnaise\n2 tbsp vanilla"""
        mock_old_doc.version = 2

        mock_new_doc = Mock()
        mock_new_doc.content = """1 cup of mayonnaise\n"""
        mock_new_doc.version = 3 

        response = document_diff.compare_docs(old_document=mock_old_doc,
                                              new_document=mock_new_doc)

        assert "--- version 2" in response
        assert "+++ version 3" in response
        assert "-2 tbsp vanilla" in response

    def test_added_new_line(self):
        mock_old_doc = Mock()
        mock_old_doc.content = """1 cup of mayonnaise\n"""
        mock_old_doc.version = 1

        mock_new_doc = Mock()
        mock_new_doc.content = """1 cup of mayonnaise\n2 tbsp vanilla"""
        mock_new_doc.version = 7

        response = document_diff.compare_docs(old_document=mock_old_doc,
                                              new_document=mock_new_doc)

        assert "--- version 1" in response
        assert "+++ version 7" in response
        assert "+2 tbsp vanilla" in response

    def test_modified_content(self):
        mock_old_doc = Mock()
        mock_old_doc.content = """1 cup of mayonnaise\n5 tbsp vanilla"""
        mock_old_doc.version = 5

        mock_new_doc = Mock()
        mock_new_doc.content = """1 cup of mayonnaise\n2 tbsp vanilla"""
        mock_new_doc.version = 7

        response = document_diff.compare_docs(old_document=mock_old_doc,
                                              new_document=mock_new_doc)

        assert "--- version 5" in response
        assert "+++ version 7" in response
        assert "-5 tbsp vanilla" in response
        assert "+2 tbsp vanilla" in response