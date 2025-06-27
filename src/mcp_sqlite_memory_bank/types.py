"""
Type definitions for SQLite Memory Bank.

This module contains type definitions and custom error classes used throughout
the project. Designed for explicit, discoverable use by LLMs and FastMCP clients.
"""

from typing import TypedDict, Dict, Any, Literal, List, Union, Optional
from dataclasses import dataclass
from enum import Enum, auto


class SqliteType(str, Enum):
    """Valid SQLite column types."""

    TEXT = "TEXT"
    INTEGER = "INTEGER"
    REAL = "REAL"
    BLOB = "BLOB"
    NULL = "NULL"
    TIMESTAMP = "TIMESTAMP"  # Common extension
    BOOLEAN = "BOOLEAN"  # Common extension


class ErrorCategory(Enum):
    """Categories for SQLite Memory Bank errors."""

    VALIDATION = auto()
    DATABASE = auto()
    SCHEMA = auto()
    DATA = auto()
    SYSTEM = auto()


@dataclass
class MemoryBankError(Exception):
    """Base class for SQLite Memory Bank errors."""

    message: str
    category: ErrorCategory
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to a dict format suitable for FastMCP responses."""
        return {"success": False, "error": self.message, "category": self.category.name, "details": self.details or {}}


class ValidationError(MemoryBankError):
    """Error for invalid inputs (table names, column names, data types, etc)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.VALIDATION, details)


class DatabaseError(MemoryBankError):
    """Error for SQLite database operations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.DATABASE, details)


class SchemaError(MemoryBankError):
    """Error for schema-related operations (create/alter table, etc)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.SCHEMA, details)


class DataError(MemoryBankError):
    """Error for data operations (insert/update/delete)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCategory.DATA, details)


class TableColumn(TypedDict):
    """Structure for table column definitions."""

    name: str
    type: str
    notnull: bool
    default: Any
    pk: bool


class SuccessResponse(TypedDict):
    """Base structure for successful responses."""

    success: Literal[True]


class ErrorResponse(TypedDict):
    """Structure for error responses."""

    success: Literal[False]
    error: str
    category: str
    details: Dict[str, Any]


class CreateTableResponse(SuccessResponse):
    """Response for create_table tool."""

    pass


class DropTableResponse(SuccessResponse):
    """Response for drop_table tool."""

    pass


class RenameTableResponse(SuccessResponse):
    """Response for rename_table tool."""

    pass


class ListTablesResponse(SuccessResponse):
    """Response for list_tables tool."""

    tables: List[str]


class DescribeTableResponse(SuccessResponse):
    """Response for describe_table tool."""

    columns: List[Dict[str, Any]]


class ListAllColumnsResponse(SuccessResponse):
    """Response for list_all_columns tool."""

    schemas: Dict[str, List[str]]


class CreateRowResponse(SuccessResponse):
    """Response for create_row tool."""

    id: int


class ReadRowsResponse(SuccessResponse):
    """Response for read_rows tool."""

    rows: List[Dict[str, Any]]


class UpdateRowsResponse(SuccessResponse):
    """Response for update_rows tool."""

    rows_affected: int


class DeleteRowsResponse(SuccessResponse):
    """Response for delete_rows tool."""

    rows_affected: int


class SelectQueryResponse(SuccessResponse):
    """Response for run_select_query tool."""

    rows: List[Dict[str, Any]]


class SearchContentResponse(SuccessResponse):
    """Response for search_content tool."""

    results: List[Dict[str, Any]]
    query: str
    tables_searched: List[str]
    total_results: int


class ExploreTablesResponse(SuccessResponse):
    """Response for explore_tables tool."""

    exploration: Dict[str, Any]


# Semantic Search Response Types
class SemanticSearchResponse(TypedDict, total=False):
    """Response type for semantic search operations."""

    success: bool
    results: List[Dict[str, Any]]
    query: str
    tables_searched: List[str]
    total_results: int
    model: str
    similarity_threshold: float
    auto_embedded_tables: List[str]  # Tables that had embeddings auto-generated
    auto_embedding_note: str  # Message about auto-embedding


class RelatedContentResponse(TypedDict, total=False):
    """Response type for find related content operations."""

    success: bool
    results: List[Dict[str, Any]]
    target_row: Dict[str, Any]
    total_results: int
    similarity_threshold: float
    model: str
    message: str  # Optional field


class HybridSearchResponse(TypedDict):
    """Response type for hybrid search operations."""

    success: bool
    results: List[Dict[str, Any]]
    query: str
    search_type: str
    semantic_weight: float
    text_weight: float
    total_results: int
    model: str


class EmbeddingStatsResponse(TypedDict):
    """Response type for embedding statistics."""

    success: bool
    table_name: str
    total_rows: int
    embedded_rows: int
    coverage_percent: float
    embedding_dimensions: Optional[int]
    embedding_column: str


class GenerateEmbeddingsResponse(TypedDict):
    """Response type for embedding generation operations."""

    success: bool
    message: str
    processed: int
    model: str
    embedding_dimension: int


class EmbeddingColumnResponse(TypedDict):
    """Response type for adding embedding columns."""

    success: bool
    message: str


# Type alias for all possible responses
ToolResponse = Union[
    CreateTableResponse,
    DropTableResponse,
    RenameTableResponse,
    ListTablesResponse,
    DescribeTableResponse,
    ListAllColumnsResponse,
    CreateRowResponse,
    ReadRowsResponse,
    UpdateRowsResponse,
    DeleteRowsResponse,
    SelectQueryResponse,
    SearchContentResponse,
    ExploreTablesResponse,
    ErrorResponse,
    SemanticSearchResponse,
    RelatedContentResponse,
    HybridSearchResponse,
    EmbeddingStatsResponse,
    GenerateEmbeddingsResponse,
    EmbeddingColumnResponse,
]
