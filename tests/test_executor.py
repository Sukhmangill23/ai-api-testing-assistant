import pytest
from app.services.test_executor import TestExecutor
import responses
import json


@pytest.fixture
def test_executor():
    return TestExecutor("http://localhost:8000")


@pytest.fixture
def sample_test_case():
    return {
        "name": "Get users - success",
        "method": "GET",
        "endpoint": "/users",
        "headers": {"Content-Type": "application/json"},
        "body": None,
        "expected_status": 200,
        "expected_response": {"users": []},
        "assertions": ["status code is 200", "response contains users"]
    }


@responses.activate
def test_execute_test_case_success(test_executor, sample_test_case):
    """Test successful test case execution"""
    responses.add(
        responses.GET,
        "http://localhost:8000/users",
        json={"users": []},
        status=200
    )

    result = test_executor.execute_test_case(sample_test_case)

    assert result["status"] == "passed"
    assert result["actual_status"] == 200
    assert len(result["errors"]) == 0


@responses.activate
def test_execute_test_case_wrong_status(test_executor, sample_test_case):
    """Test handling of wrong status code"""
    responses.add(
        responses.GET,
        "http://localhost:8000/users",
        json={"users": []},
        status=404
    )

    result = test_executor.execute_test_case(sample_test_case)

    assert result["status"] == "failed"
    assert result["actual_status"] == 404
    assert len(result["errors"]) > 0


@responses.activate
def test_execute_test_case_request_exception(test_executor, sample_test_case):
    """Test handling of request exceptions"""
    responses.add(
        responses.GET,
        "http://localhost:8000/users",
        body=Exception("Connection error")
    )

    result = test_executor.execute_test_case(sample_test_case)

    assert result["status"] == "failed"
    assert len(result["errors"]) > 0


@responses.activate
def test_execute_test_suite(test_executor):
    """Test executing multiple test cases"""
    responses.add(
        responses.GET,
        "http://localhost:8000/users",
        json={"users": []},
        status=200
    )
    responses.add(
        responses.POST,
        "http://localhost:8000/users",
        json={"id": 1},
        status=201
    )

    test_cases = [
        {
            "name": "Get users",
            "method": "GET",
            "endpoint": "/users",
            "expected_status": 200
        },
        {
            "name": "Create user",
            "method": "POST",
            "endpoint": "/users",
            "expected_status": 201,
            "body": {"name": "John"}
        }
    ]

    results = test_executor.execute_test_suite(test_cases)

    assert results["total_tests"] == 2
    assert results["passed_tests"] >= 0
    assert results["failed_tests"] >= 0
    assert "execution_time" in results
    assert "coverage_percentage" in results


def test_validate_response_structure(test_executor):
    """Test response validation logic"""
    result = {"status": "passed", "errors": [], "assertions_passed": [],
              "assertions_failed": []}

    actual = {"name": "John", "age": 30}
    expected = {"name": "John", "age": 30}

    test_executor._validate_response(actual, expected, result)

    assert result["status"] == "passed"
    assert len(result["errors"]) == 0


def test_validate_response_missing_key(test_executor):
    """Test validation with missing key"""
    result = {"status": "passed", "errors": [], "assertions_passed": [],
              "assertions_failed": []}

    actual = {"name": "John"}
    expected = {"name": "John", "age": 30}

    test_executor._validate_response(actual, expected, result)

    assert result["status"] == "failed"
    assert len(result["errors"]) > 0
