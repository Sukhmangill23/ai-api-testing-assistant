import pytest
from unittest.mock import Mock, patch
from app.services.ai_service import AIService
import json


@pytest.fixture
def ai_service():
    return AIService()


@pytest.fixture
def sample_openapi_spec():
    return {
        "path": "/users",
        "method": "GET",
        "parameters": [],
        "responses": {
            "200": {
                "description": "Success",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                }
            }
        }
    }


@patch('app.services.ai_service.ollama.Client')
def test_generate_test_cases_success(mock_client_class, ai_service,
                                     sample_openapi_spec):
    """Test successful test case generation"""
    # Mock Ollama response
    mock_response = {
        'message': {
            'content': json.dumps([
                {
                    "name": "Get all users - success",
                    "method": "GET",
                    "endpoint": "/users",
                    "headers": {},
                    "body": None,
                    "expected_status": 200,
                    "expected_response": {"type": "array"},
                    "assertions": ["response is array"]
                }
            ])
        }
    }

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    ai_service.client = mock_client

    # Generate tests
    test_cases = ai_service.generate_test_cases(
        sample_openapi_spec,
        "/users",
        "GET",
        include_edge_cases=True
    )

    assert len(test_cases) > 0
    assert test_cases[0]["name"] == "Get all users - success"
    assert test_cases[0]["method"] == "GET"


@patch('app.services.ai_service.ollama.Client')
def test_generate_test_cases_with_markdown(mock_client_class, ai_service,
                                           sample_openapi_spec):
    """Test handling of markdown code blocks in response"""
    mock_response = {
        'message': {
            'content': '```json\n[{"name": "test"}]\n```'
        }
    }

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    ai_service.client = mock_client

    test_cases = ai_service.generate_test_cases(
        sample_openapi_spec, "/users", "GET"
    )

    assert len(test_cases) > 0


@patch('app.services.ai_service.ollama.Client')
def test_generate_test_cases_handles_errors(mock_client_class, ai_service,
                                            sample_openapi_spec):
    """Test error handling in test case generation"""
    mock_client = Mock()
    mock_client.chat.side_effect = Exception("API Error")
    mock_client_class.return_value = mock_client

    ai_service.client = mock_client

    test_cases = ai_service.generate_test_cases(
        sample_openapi_spec, "/users", "GET"
    )
    assert test_cases == []


@patch('app.services.ai_service.ollama.Client')
def test_analyze_test_results(mock_client_class, ai_service):
    """Test analysis of test results"""
    mock_response = {
        'message': {
            'content': json.dumps({
                "overall_quality_score": 85,
                "critical_issues": ["Missing authentication tests"],
                "failure_patterns": [],
                "recommendations": ["Add more edge cases"],
                "well_covered_areas": ["Happy path scenarios"],
                "coverage_gaps": ["Error handling"],
                "summary": "Good coverage overall"
            })
        }
    }

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    ai_service.client = mock_client

    results = [
        {"name": "test1", "status": "passed"},
        {"name": "test2", "status": "failed"}
    ]

    analysis = ai_service.analyze_test_results(results)

    assert analysis["overall_quality_score"] == 85
    assert "Missing authentication tests" in analysis["critical_issues"]
