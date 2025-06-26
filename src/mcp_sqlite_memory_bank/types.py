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
    BOOLEAN = "BOOLEAN"      # Common extension


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
        return {
            "success": False,
            "error": self.message,
            "category": self.category.name,
            "details": self.details or {}
        }


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
    columns: List[TableColumn]


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
    ErrorResponse
]
