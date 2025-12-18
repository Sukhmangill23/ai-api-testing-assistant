import pytest
from app.services.test_generator import TestGenerator
from unittest.mock import Mock, patch
import json


@pytest.fixture
def test_generator():
    return TestGenerator()


@pytest.fixture
def sample_spec():
    return json.dumps({
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get users",
                    "responses": {
                        "200": {"description": "Success"}
                    }
                }
            },
            "/users/{id}": {
                "get": {
                    "summary": "Get user by ID",
                    "parameters": [
                        {"name": "id", "in": "path", "required": True}
                    ],
                    "responses": {
                        "200": {"description": "Success"},
                        "404": {"description": "Not found"}
                    }
                }
            }
        }
    })


@patch('app.services.test_generator.AIService')
def test_generate_tests_for_spec(mock_ai_service, test_generator, sample_spec):
    """Test generating tests for entire spec"""
    mock_ai = Mock()
    mock_ai.generate_test_cases.return_value = [
        {
            "name": "Test case 1",
            "method": "GET",
            "endpoint": "/users",
            "expected_status": 200
        }
    ]
    mock_ai_service.return_value = mock_ai

    test_generator.ai_service = mock_ai

    tests = test_generator.generate_tests_for_spec(sample_spec,
                                                   include_edge_cases=True)

    assert len(tests) >= 2  # At least 2 endpoints
    assert mock_ai.generate_test_cases.called


def test_generate_tests_handles_invalid_json(test_generator):
    """Test handling of invalid JSON spec"""
    tests = test_generator.generate_tests_for_spec("invalid json",
                                                   include_edge_cases=True)
    assert tests == []


@patch('app.services.test_generator.AIService')
def test_generate_tests_no_edge_cases(mock_ai_service, test_generator,
                                      sample_spec):
    """Test generating tests without edge cases"""
    mock_ai = Mock()
    mock_ai.generate_test_cases.return_value = [{"name": "Basic test"}]
    mock_ai_service.return_value = mock_ai

    test_generator.ai_service = mock_ai

    tests = test_generator.generate_tests_for_spec(sample_spec,
                                                   include_edge_cases=False)

    # Verify edge_cases parameter was passed correctly
    call_args = mock_ai.generate_test_cases.call_args_list
    for call in call_args:
        assert call[1]['include_edge_cases'] == False
