"""
Comprehensive tests for centralized embedding filtering utilities.
Tests ensure proper filtering of embedding data across all modules.
"""
import pytest
from typing import List, Dict, Any, Optional
from unittest.mock import Mock

from mcp_sqlite_memory_bank.utils import (
    filter_embedding_columns,
    filter_embedding_from_row,
    filter_embedding_from_rows,
    get_content_columns
)


class TestFilterEmbeddingColumns:
    """Test filter_embedding_columns function."""
    
    def test_filters_embedding_column(self):
        """Test that embedding column is filtered out."""
        columns = ['id', 'name', 'embedding', 'content']
        result = filter_embedding_columns(columns)
        assert result == ['id', 'name', 'content']
        assert 'embedding' not in result
    
    def test_no_embedding_column(self):
        """Test behavior when no embedding column exists."""
        columns = ['id', 'name', 'content']
        result = filter_embedding_columns(columns)
        assert result == ['id', 'name', 'content']
    
    def test_empty_list(self):
        """Test behavior with empty column list."""
        columns = []
        result = filter_embedding_columns(columns)
        assert result == []
    
    def test_only_embedding_column(self):
        """Test behavior when only embedding column exists."""
        columns = ['embedding']
        result = filter_embedding_columns(columns)
        assert result == []
    
    def test_multiple_embedding_columns(self):
        """Test behavior with multiple embedding columns (edge case)."""
        columns = ['id', 'embedding', 'content', 'embedding_backup']
        result = filter_embedding_columns(columns)
        # Should only filter 'embedding', not 'embedding_backup'
        assert result == ['id', 'content', 'embedding_backup']
    
    def test_preserves_order(self):
        """Test that column order is preserved."""
        columns = ['z_col', 'a_col', 'embedding', 'm_col']
        result = filter_embedding_columns(columns)
        assert result == ['z_col', 'a_col', 'm_col']


class TestFilterEmbeddingFromRow:
    """Test filter_embedding_from_row function."""
    
    def test_filters_embedding_from_dict(self):
        """Test embedding filtering from dictionary row."""
        row = {
            'id': 1,
            'name': 'test',
            'embedding': [0.1, 0.2, 0.3],
            'content': 'sample content'
        }
        result = filter_embedding_from_row(row)
        expected = {
            'id': 1,
            'name': 'test',
            'content': 'sample content'
        }
        assert result == expected
        assert 'embedding' not in result
    
    def test_no_embedding_in_row(self):
        """Test behavior when row has no embedding column."""
        row = {
            'id': 1,
            'name': 'test',
            'content': 'sample content'
        }
        result = filter_embedding_from_row(row)
        assert result == row  # Should be unchanged
    
    def test_empty_row(self):
        """Test behavior with empty row."""
        row = {}
        result = filter_embedding_from_row(row)
        assert result == {}
    
    def test_only_embedding_in_row(self):
        """Test behavior when row only contains embedding."""
        row = {'embedding': [0.1, 0.2, 0.3]}
        result = filter_embedding_from_row(row)
        assert result == {}
    
    def test_preserves_other_data_types(self):
        """Test that non-embedding data types are preserved."""
        row = {
            'id': 1,
            'name': 'test',
            'active': True,
            'score': 95.5,
            'tags': ['tag1', 'tag2'],
            'metadata': {'key': 'value'},
            'embedding': [0.1, 0.2]
        }
        result = filter_embedding_from_row(row)
        expected = {
            'id': 1,
            'name': 'test',
            'active': True,
            'score': 95.5,
            'tags': ['tag1', 'tag2'],
            'metadata': {'key': 'value'}
        }
        assert result == expected
    
    def test_none_row_handling(self):
        """Test behavior with None row (defensive programming)."""
        # This tests the function's robustness
        with pytest.raises(AttributeError):
            filter_embedding_from_row(None)  # type: ignore


class TestFilterEmbeddingFromRows:
    """Test filter_embedding_from_rows function."""
    
    def test_filters_embedding_from_multiple_rows(self):
        """Test embedding filtering from list of rows."""
        rows = [
            {
                'id': 1,
                'name': 'test1',
                'embedding': [0.1, 0.2],
                'content': 'content1'
            },
            {
                'id': 2,
                'name': 'test2',
                'embedding': [0.3, 0.4],
                'content': 'content2'
            }
        ]
        result = filter_embedding_from_rows(rows)
        expected = [
            {
                'id': 1,
                'name': 'test1',
                'content': 'content1'
            },
            {
                'id': 2,
                'name': 'test2',
                'content': 'content2'
            }
        ]
        assert result == expected
        # Verify no embedding columns in any row
        for row in result:
            assert 'embedding' not in row
    
    def test_empty_rows_list(self):
        """Test behavior with empty rows list."""
        rows = []
        result = filter_embedding_from_rows(rows)
        assert result == []
    
    def test_mixed_rows_with_and_without_embedding(self):
        """Test rows where some have embedding and some don't."""
        rows = [
            {
                'id': 1,
                'name': 'test1',
                'embedding': [0.1, 0.2],
                'content': 'content1'
            },
            {
                'id': 2,
                'name': 'test2',
                'content': 'content2'  # No embedding
            }
        ]
        result = filter_embedding_from_rows(rows)
        expected = [
            {
                'id': 1,
                'name': 'test1',
                'content': 'content1'
            },
            {
                'id': 2,
                'name': 'test2',
                'content': 'content2'
            }
        ]
        assert result == expected
    
    def test_preserves_row_order(self):
        """Test that row order is preserved."""
        rows = [
            {'id': 3, 'embedding': [0.1]},
            {'id': 1, 'embedding': [0.2]},
            {'id': 2, 'embedding': [0.3]}
        ]
        result = filter_embedding_from_rows(rows)
        expected = [
            {'id': 3},
            {'id': 1},
            {'id': 2}
        ]
        assert result == expected


class TestGetContentColumns:
    """Test get_content_columns function."""
    
    def test_identifies_content_columns(self):
        """Test identification of content columns."""
        columns = ['id', 'title', 'content', 'score', 'embedding', 'timestamp', 'description']
        result = get_content_columns(columns)
        expected = ['title', 'content', 'score', 'description']
        assert result == expected
        assert 'embedding' not in result
        assert 'id' not in result  # System column
        assert 'timestamp' not in result  # System column
    
    def test_filters_system_columns(self):
        """Test filtering of system columns."""
        columns = ['id', 'embedding', 'timestamp', 'content', 'title']
        result = get_content_columns(columns)
        expected = ['content', 'title']
        assert result == expected
    
    def test_empty_column_list(self):
        """Test behavior with empty column list."""
        columns = []
        result = get_content_columns(columns)
        assert result == []
    
    def test_only_system_columns(self):
        """Test behavior when only system columns exist."""
        columns = ['id', 'embedding', 'timestamp']
        result = get_content_columns(columns)
        assert result == []
    
    def test_preserves_column_order(self):
        """Test that column order is preserved."""
        columns = ['z_content', 'a_title', 'id', 'embedding', 'm_description']
        result = get_content_columns(columns)
        expected = ['z_content', 'a_title', 'm_description']
        assert result == expected


class TestIntegrationScenarios:
    """Integration tests for real-world usage scenarios."""
    
    def test_database_query_filtering_workflow(self):
        """Test typical database query result filtering workflow."""
        # Simulate database query results
        columns = ['id', 'title', 'content', 'embedding', 'created_at']
        rows = [
            {
                'id': 1,
                'title': 'Test Document',
                'content': 'Sample content',
                'embedding': [0.1, 0.2, 0.3],
                'created_at': '2024-01-01'
            },
            {
                'id': 2,
                'title': 'Another Document',
                'content': 'More content',
                'embedding': [0.4, 0.5, 0.6],
                'created_at': '2024-01-02'
            }
        ]
        
        # Filter columns
        filtered_columns = filter_embedding_columns(columns)
        assert filtered_columns == ['id', 'title', 'content', 'created_at']
        
        # Filter rows
        filtered_rows = filter_embedding_from_rows(rows)
        expected_rows = [
            {
                'id': 1,
                'title': 'Test Document',
                'content': 'Sample content',
                'created_at': '2024-01-01'
            },
            {
                'id': 2,
                'title': 'Another Document',
                'content': 'More content',
                'created_at': '2024-01-02'
            }
        ]
        assert filtered_rows == expected_rows
    
    def test_semantic_search_result_filtering(self):
        """Test filtering of semantic search results."""
        # Simulate semantic search results with similarity scores
        search_results = [
            {
                'id': 1,
                'content': 'Machine learning algorithms',
                'embedding': [0.8, 0.2, 0.1],
                'similarity_score': 0.95
            },
            {
                'id': 2,
                'content': 'Deep neural networks',
                'embedding': [0.7, 0.3, 0.0],
                'similarity_score': 0.87
            }
        ]
        
        filtered_results = filter_embedding_from_rows(search_results)
        expected_results = [
            {
                'id': 1,
                'content': 'Machine learning algorithms',
                'similarity_score': 0.95
            },
            {
                'id': 2,
                'content': 'Deep neural networks',
                'similarity_score': 0.87
            }
        ]
        assert filtered_results == expected_results
    
    def test_api_response_preparation(self):
        """Test preparation of API responses with embedding filtering."""
        # Simulate raw database data that needs to be returned to API clients
        raw_data = {
            'success': True,
            'rows': [
                {
                    'id': 1,
                    'title': 'Document Title',
                    'content': 'Document content here',
                    'embedding': [0.1, 0.2, 0.3, 0.4],
                    'metadata': {'type': 'article'}
                }
            ],
            'total_count': 1
        }
        
        # Filter embedding data from rows
        filtered_data = raw_data.copy()
        filtered_data['rows'] = filter_embedding_from_rows(raw_data['rows'])
        
        expected_data = {
            'success': True,
            'rows': [
                {
                    'id': 1,
                    'title': 'Document Title',
                    'content': 'Document content here',
                    'metadata': {'type': 'article'}
                }
            ],
            'total_count': 1
        }
        assert filtered_data == expected_data


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_malformed_row_data(self):
        """Test handling of malformed row data."""
        # Test with non-dict row (should raise error)
        with pytest.raises(AttributeError):
            filter_embedding_from_row("not a dict")  # type: ignore
        
        with pytest.raises(AttributeError):
            filter_embedding_from_row(123)  # type: ignore
    
    def test_large_embedding_vectors(self):
        """Test handling of large embedding vectors."""
        row = {
            'id': 1,
            'content': 'test',
            'embedding': [0.1] * 1536  # Large embedding vector
        }
        result = filter_embedding_from_row(row)
        assert result == {'id': 1, 'content': 'test'}
        assert 'embedding' not in result
    
    def test_nested_embedding_data(self):
        """Test that nested embedding data is not accidentally filtered."""
        row = {
            'id': 1,
            'metadata': {
                'embedding_model': 'sentence-transformers',
                'embedding_dim': 384
            },
            'embedding': [0.1, 0.2, 0.3]
        }
        result = filter_embedding_from_row(row)
        expected = {
            'id': 1,
            'metadata': {
                'embedding_model': 'sentence-transformers',
                'embedding_dim': 384
            }
        }
        assert result == expected


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
