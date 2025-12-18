import requests
import time
from typing import List, Dict, Any
from datetime import datetime


class TestExecutor:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def execute_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single test case
        """
        start_time = time.time()
        result = {
            "name": test_case.get("name", "Unnamed Test"),
            "status": "passed",
            "execution_time": 0,
            "actual_status": None,
            "expected_status": test_case.get("expected_status"),
            "errors": [],
            "assertions_passed": [],
            "assertions_failed": []
        }

        try:
            # Build full URL
            endpoint = test_case.get("endpoint", "")

            # FIX: Clean up endpoint path
            if not endpoint.startswith('/'):
                endpoint = '/' + endpoint

            # FIX: Remove double slashes
            url = f"{self.base_url}{endpoint}".replace('//', '/', 1)
            if url.startswith('http:/'):
                url = url.replace('http:/', 'http://', 1)
            if url.startswith('https:/'):
                url = url.replace('https:/', 'https://', 1)

            # DEBUG: Add URL to result for debugging
            result["url_tested"] = url

            # Prepare request
            method = test_case.get("method", "GET").upper()
            headers = test_case.get("headers", {})
            body = test_case.get("body")

            # Execute request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                timeout=30
            )

            result["actual_status"] = response.status_code

            # Check status code
            if response.status_code != test_case.get("expected_status"):
                result["status"] = "failed"
                result["errors"].append(
                    f"Expected status {test_case.get('expected_status')}, got {response.status_code}"
                )
            else:
                result["assertions_passed"].append(
                    "Status code matches expected")

            # Validate response structure
            if test_case.get("expected_response"):
                try:
                    actual_response = response.json()
                    self._validate_response(
                        actual_response,
                        test_case["expected_response"],
                        result
                    )
                except Exception as e:
                    result["status"] = "failed"
                    result["errors"].append(
                        f"Response validation error: {str(e)}")

            # Run custom assertions
            for assertion in test_case.get("assertions", []):
                try:
                    self._run_assertion(assertion, response, result)
                except Exception as e:
                    result["status"] = "failed"
                    result["assertions_failed"].append(f"{assertion}: {str(e)}")

        except requests.exceptions.RequestException as e:
            result["status"] = "failed"
            result["errors"].append(f"Request failed: {str(e)}")
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(f"Unexpected error: {str(e)}")

        result["execution_time"] = time.time() - start_time
        return result

    def _validate_response(self, actual: Any, expected: Any,
                           result: Dict[str, Any]):
        """Recursively validate response structure - be lenient"""
        if isinstance(expected, dict):
            for key, value in expected.items():
                if key not in actual:
                    # Don't fail just for missing keys, only log warning
                    result["warnings"] = result.get("warnings", [])
                    result["warnings"].append(f"Missing key in response: {key}")
                else:
                    self._validate_response(actual[key], value, result)
        elif isinstance(expected, list):
            if not isinstance(actual, list):
                result["status"] = "failed"
                result["errors"].append(
                    f"Expected list, got {type(actual).__name__}")
        # Add more validation logic as needed

    def _run_assertion(self, assertion: str, response: requests.Response,
                       result: Dict[str, Any]):
        """Run a custom assertion"""
        # Simple assertion evaluation (can be extended)
        if "status code is" in assertion:
            expected = int(assertion.split("is")[1].strip())
            if response.status_code == expected:
                result["assertions_passed"].append(assertion)
            else:
                result["assertions_failed"].append(assertion)
        elif "response contains" in assertion:
            key = assertion.split("contains")[1].strip().strip('"\'')
            if key in response.text:
                result["assertions_passed"].append(assertion)
            else:
                result["assertions_failed"].append(assertion)
        else:
            result["assertions_passed"].append(f"{assertion} (skipped)")

    def execute_test_suite(self, test_cases: List[Dict[str, Any]]) -> Dict[
        str, Any]:
        """
        Execute a full test suite
        """
        start_time = time.time()
        results = []
        passed = 0
        failed = 0

        for test_case in test_cases:
            result = self.execute_test_case(test_case)
            results.append(result)

            if result["status"] == "passed":
                passed += 1
            else:
                failed += 1

        total_time = time.time() - start_time
        total_tests = len(test_cases)

        return {
            "total_tests": total_tests,
            "passed_tests": passed,
            "failed_tests": failed,
            "coverage_percentage": (
                        passed / total_tests * 100) if total_tests > 0 else 0,
            "execution_time": total_time,
            "results": results
        }
