"""
Bulk metadata update operations.

Allows updating metadata for signed documents without re-signing.
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class MetadataUpdate:
    """Metadata update operation."""
    field: str
    value: Any
    operation: str = "set"  # set, append, remove
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "field": self.field,
            "value": self.value,
            "operation": self.operation
        }


@dataclass
class UpdateResult:
    """Result of a metadata update operation."""
    document_id: str
    success: bool
    updates_applied: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "success": self.success,
            "updates_applied": self.updates_applied,
            "error": self.error
        }


@dataclass
class BulkUpdateResult:
    """Result of bulk update operation."""
    total_documents: int
    successful: int
    failed: int
    updates: List[UpdateResult]
    total_time: float
    
    def summary(self) -> str:
        """Generate summary string."""
        success_rate = (self.successful / self.total_documents * 100) if self.total_documents > 0 else 0
        return (
            f"Bulk Update Complete:\n"
            f"  Total: {self.total_documents}\n"
            f"  Successful: {self.successful}\n"
            f"  Failed: {self.failed}\n"
            f"  Success Rate: {success_rate:.1f}%\n"
            f"  Time: {self.total_time:.2f}s"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_documents": self.total_documents,
            "successful": self.successful,
            "failed": self.failed,
            "updates": [u.to_dict() for u in self.updates],
            "total_time": self.total_time
        }


class MetadataValidator:
    """
    Validate metadata updates before applying.
    
    Example:
        >>> validator = MetadataValidator()
        >>> is_valid = validator.validate_update("author", "John Doe")
    """
    
    # Allowed metadata fields
    ALLOWED_FIELDS = {
        "author", "publisher", "license", "title", "description",
        "keywords", "category", "tags", "custom"
    }
    
    # Read-only fields that cannot be updated
    READONLY_FIELDS = {
        "document_id", "signature_timestamp", "signer_id",
        "organization_id", "content_hash"
    }
    
    def validate_update(
        self,
        field: str,
        value: Any,
        operation: str = "set"
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a metadata update.
        
        Args:
            field: Field name to update
            value: New value
            operation: Operation type (set, append, remove)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if field is read-only
        if field in self.READONLY_FIELDS:
            return False, f"Field '{field}' is read-only and cannot be updated"
        
        # Check if field is allowed
        if field not in self.ALLOWED_FIELDS and not field.startswith("custom."):
            return False, f"Field '{field}' is not allowed for updates"
        
        # Validate operation
        if operation not in ["set", "append", "remove"]:
            return False, f"Invalid operation '{operation}'. Must be 'set', 'append', or 'remove'"
        
        # Validate value type for append operation
        if operation == "append" and not isinstance(value, (list, str)):
            return False, "Append operation requires list or string value"
        
        return True, None
    
    def validate_batch(
        self,
        updates: List[MetadataUpdate]
    ) -> tuple[bool, List[str]]:
        """
        Validate a batch of updates.
        
        Args:
            updates: List of metadata updates
        
        Returns:
            Tuple of (all_valid, error_messages)
        """
        errors = []
        
        for update in updates:
            is_valid, error = self.validate_update(
                update.field,
                update.value,
                update.operation
            )
            if not is_valid:
                errors.append(error)
        
        return len(errors) == 0, errors


class BulkMetadataUpdater:
    """
    Perform bulk metadata updates on signed documents.
    
    Example:
        >>> from encypher_enterprise import EncypherClient
        >>> client = EncypherClient(api_key="...")
        >>> updater = BulkMetadataUpdater(client)
        >>> 
        >>> # Update single field
        >>> result = updater.update_metadata(
        ...     document_id="doc_123",
        ...     updates=[MetadataUpdate("author", "Jane Doe")]
        ... )
        >>> 
        >>> # Bulk update multiple documents
        >>> result = updater.bulk_update(
        ...     document_ids=["doc_1", "doc_2", "doc_3"],
        ...     updates=[MetadataUpdate("publisher", "Acme Corp")]
        ... )
    """
    
    def __init__(self, client):
        """
        Initialize bulk updater.
        
        Args:
            client: Encypher client instance
        """
        self.client = client
        self.validator = MetadataValidator()
    
    def update_metadata(
        self,
        document_id: str,
        updates: List[MetadataUpdate],
        validate: bool = True
    ) -> UpdateResult:
        """
        Update metadata for a single document.
        
        Args:
            document_id: Document ID to update
            updates: List of metadata updates
            validate: Validate updates before applying
        
        Returns:
            UpdateResult with operation status
        """
        # Validate updates if requested
        if validate:
            is_valid, errors = self.validator.validate_batch(updates)
            if not is_valid:
                return UpdateResult(
                    document_id=document_id,
                    success=False,
                    error="; ".join(errors)
                )
        
        try:
            # Prepare update payload
            update_data = {
                "document_id": document_id,
                "updates": [u.to_dict() for u in updates]
            }
            
            # Call API (placeholder - actual API endpoint needed)
            # response = self.client._post("/v1/documents/update-metadata", update_data)
            
            # For now, return success (API integration needed)
            return UpdateResult(
                document_id=document_id,
                success=True,
                updates_applied=len(updates)
            )
        
        except Exception as e:
            return UpdateResult(
                document_id=document_id,
                success=False,
                error=str(e)
            )
    
    def bulk_update(
        self,
        document_ids: List[str],
        updates: List[MetadataUpdate],
        validate: bool = True,
        continue_on_error: bool = True
    ) -> BulkUpdateResult:
        """
        Update metadata for multiple documents.
        
        Args:
            document_ids: List of document IDs
            updates: List of metadata updates to apply to all documents
            validate: Validate updates before applying
            continue_on_error: Continue processing if one update fails
        
        Returns:
            BulkUpdateResult with operation status
        """
        import time
        start_time = time.time()
        
        results = []
        
        for doc_id in document_ids:
            result = self.update_metadata(doc_id, updates, validate)
            results.append(result)
            
            # Stop on first error if continue_on_error is False
            if not continue_on_error and not result.success:
                break
        
        total_time = time.time() - start_time
        
        return BulkUpdateResult(
            total_documents=len(document_ids),
            successful=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            updates=results,
            total_time=total_time
        )
    
    def update_from_file(
        self,
        updates_file: Path,
        validate: bool = True
    ) -> BulkUpdateResult:
        """
        Load updates from JSON file and apply them.
        
        File format:
        {
            "documents": [
                {
                    "document_id": "doc_123",
                    "updates": [
                        {"field": "author", "value": "Jane Doe", "operation": "set"}
                    ]
                }
            ]
        }
        
        Args:
            updates_file: Path to JSON file with updates
            validate: Validate updates before applying
        
        Returns:
            BulkUpdateResult with operation status
        """
        import time
        start_time = time.time()
        
        # Load updates from file
        with open(updates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        
        for doc_data in data.get("documents", []):
            doc_id = doc_data["document_id"]
            updates = [
                MetadataUpdate(
                    field=u["field"],
                    value=u["value"],
                    operation=u.get("operation", "set")
                )
                for u in doc_data.get("updates", [])
            ]
            
            result = self.update_metadata(doc_id, updates, validate)
            results.append(result)
        
        total_time = time.time() - start_time
        
        return BulkUpdateResult(
            total_documents=len(results),
            successful=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
            updates=results,
            total_time=total_time
        )
    
    def update_by_query(
        self,
        query: Dict[str, Any],
        updates: List[MetadataUpdate],
        validate: bool = True,
        max_documents: int = 1000
    ) -> BulkUpdateResult:
        """
        Update documents matching a query.
        
        Args:
            query: Query to match documents (e.g., {"author": "Old Name"})
            updates: Updates to apply
            validate: Validate updates
            max_documents: Maximum documents to update
        
        Returns:
            BulkUpdateResult with operation status
        """
        # This would query the API for matching documents
        # For now, return empty result (API integration needed)
        return BulkUpdateResult(
            total_documents=0,
            successful=0,
            failed=0,
            updates=[],
            total_time=0.0
        )


def create_update_template(output_file: Path) -> None:
    """
    Create a template JSON file for bulk updates.
    
    Args:
        output_file: Path to save template
    """
    template = {
        "documents": [
            {
                "document_id": "doc_123",
                "updates": [
                    {
                        "field": "author",
                        "value": "Jane Doe",
                        "operation": "set"
                    },
                    {
                        "field": "tags",
                        "value": ["news", "technology"],
                        "operation": "append"
                    }
                ]
            },
            {
                "document_id": "doc_456",
                "updates": [
                    {
                        "field": "publisher",
                        "value": "Acme Corp",
                        "operation": "set"
                    }
                ]
            }
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2)


def validate_update_file(updates_file: Path) -> tuple[bool, List[str]]:
    """
    Validate a bulk update JSON file.
    
    Args:
        updates_file: Path to JSON file
    
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        with open(updates_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except FileNotFoundError:
        return False, [f"File not found: {updates_file}"]
    
    # Validate structure
    if "documents" not in data:
        errors.append("Missing 'documents' key in root object")
        return False, errors
    
    if not isinstance(data["documents"], list):
        errors.append("'documents' must be an array")
        return False, errors
    
    # Validate each document
    validator = MetadataValidator()
    
    for i, doc in enumerate(data["documents"]):
        if "document_id" not in doc:
            errors.append(f"Document {i}: Missing 'document_id'")
            continue
        
        if "updates" not in doc:
            errors.append(f"Document {i}: Missing 'updates'")
            continue
        
        for j, update in enumerate(doc["updates"]):
            if "field" not in update:
                errors.append(f"Document {i}, Update {j}: Missing 'field'")
                continue
            
            if "value" not in update:
                errors.append(f"Document {i}, Update {j}: Missing 'value'")
                continue
            
            operation = update.get("operation", "set")
            is_valid, error = validator.validate_update(
                update["field"],
                update["value"],
                operation
            )
            
            if not is_valid:
                errors.append(f"Document {i}, Update {j}: {error}")
    
    return len(errors) == 0, errors
