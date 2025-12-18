from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class APISpecCreate(BaseModel):
    name: str
    spec_content: str  # JSON string of OpenAPI spec


class APISpecResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TestCase(BaseModel):
    name: str
    method: str
    endpoint: str
    headers: Dict[str, str] = {}
    body: Optional[Dict[str, Any]] = None
    expected_status: int
    expected_response: Optional[Dict[str, Any]] = None
    assertions: List[str] = []


class TestSuiteCreate(BaseModel):
    api_spec_id: int
    name: str
    description: Optional[str] = None


class TestSuiteResponse(BaseModel):
    id: int
    api_spec_id: int
    name: str
    description: Optional[str]
    generated_tests: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class TestExecutionResponse(BaseModel):
    id: int
    test_suite_id: int
    status: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    coverage_percentage: float
    execution_time: float
    results: List[Dict[str, Any]]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class GenerateTestsRequest(BaseModel):
    api_spec_id: int
    base_url: str = "http://localhost:8000"
    include_edge_cases: bool = True


class ExecuteTestsRequest(BaseModel):
    test_suite_id: int
    base_url: str
