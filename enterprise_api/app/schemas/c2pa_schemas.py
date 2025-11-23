"""
Pydantic schemas for C2PA custom assertions API.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


# Schema Management Schemas

class C2PASchemaCreate(BaseModel):
    """Request schema for creating a C2PA assertion schema."""
    namespace: str = Field(..., description="Namespace for the schema (e.g., 'com.acme')")
    label: str = Field(..., description="Full assertion label (e.g., 'com.acme.legal.v1')")
    version: str = Field(..., description="Schema version (e.g., 'v1', '1.0.0')")
    schema: Dict[str, Any] = Field(..., description="JSON Schema for validation")
    description: Optional[str] = Field(None, description="Human-readable description")
    is_public: bool = Field(False, description="Whether schema is publicly accessible")


class C2PASchemaUpdate(BaseModel):
    """Request schema for updating a C2PA assertion schema."""
    schema: Optional[Dict[str, Any]] = Field(None, description="Updated JSON Schema")
    description: Optional[str] = Field(None, description="Updated description")
    is_public: Optional[bool] = Field(None, description="Updated public flag")


class C2PASchemaResponse(BaseModel):
    """Response schema for C2PA assertion schema."""
    id: str
    namespace: str
    label: str
    version: str
    schema: Dict[str, Any]
    description: Optional[str]
    organization_id: Optional[str]
    is_public: bool
    created_at: str
    updated_at: str


class C2PASchemaListResponse(BaseModel):
    """Response schema for listing C2PA schemas."""
    schemas: List[C2PASchemaResponse]
    total: int
    page: int
    page_size: int


# Assertion Validation Schemas

class C2PAAssertionValidateRequest(BaseModel):
    """Request schema for validating a C2PA assertion."""
    label: str = Field(..., description="Assertion label to validate")
    data: Dict[str, Any] = Field(..., description="Assertion data to validate")


class C2PAAssertionValidationResult(BaseModel):
    """Validation result for a single assertion."""
    label: str
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class C2PAAssertionValidateResponse(BaseModel):
    """Response schema for assertion validation."""
    valid: bool
    assertions: List[C2PAAssertionValidationResult]


# Template Schemas

class C2PATemplateCreate(BaseModel):
    """Request schema for creating an assertion template."""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    assertions: List[Dict[str, Any]] = Field(..., description="List of assertion configurations")
    category: Optional[str] = Field(None, description="Template category (news, legal, academic, publisher)")
    is_public: bool = Field(False, description="Whether template is publicly accessible")


class C2PATemplateUpdate(BaseModel):
    """Request schema for updating an assertion template."""
    name: Optional[str] = Field(None, description="Updated name")
    description: Optional[str] = Field(None, description="Updated description")
    assertions: Optional[List[Dict[str, Any]]] = Field(None, description="Updated assertions")
    category: Optional[str] = Field(None, description="Updated category")
    is_public: Optional[bool] = Field(None, description="Updated public flag")


class C2PATemplateResponse(BaseModel):
    """Response schema for assertion template."""
    id: str
    name: str
    description: Optional[str]
    assertions: List[Dict[str, Any]]
    organization_id: Optional[str]
    is_public: bool
    category: Optional[str]
    created_at: str
    updated_at: str


class C2PATemplateListResponse(BaseModel):
    """Response schema for listing templates."""
    templates: List[C2PATemplateResponse]
    total: int
    page: int
    page_size: int


# Enhanced Embedding Request with Custom Assertions

class CustomAssertion(BaseModel):
    """Custom C2PA assertion."""
    label: str = Field(..., description="Assertion label (e.g., 'c2pa.location.v1')")
    data: Dict[str, Any] = Field(..., description="Assertion data")


class EnhancedEncodeRequest(BaseModel):
    """Enhanced encoding request with custom assertions support."""
    text: str = Field(..., description="Text content to encode")
    document_id: str = Field(..., description="Unique document identifier")
    action: str = Field("c2pa.created", description="C2PA action (e.g., 'c2pa.created', 'c2pa.edited')")
    previous_instance_id: Optional[str] = Field(None, description="Previous version instance ID for edit tracking")
    custom_assertions: Optional[List[CustomAssertion]] = Field(None, description="Custom C2PA assertions to include")
    template_id: Optional[str] = Field(None, description="Template ID to use for assertions")
    validate_assertions: bool = Field(True, description="Whether to validate custom assertions")
