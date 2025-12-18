from typing import List, Dict, Any
import json
from app.utils.openapi_parser import OpenAPIParser
from app.services.ai_service import AIService


class TestGenerator:
    def __init__(self):
        self.ai_service = AIService()

    def generate_tests_for_spec(self, spec_content: str,
                                include_edge_cases: bool = True) -> List[
        Dict[str, Any]]:
        """
        Generate test cases for all endpoints in an OpenAPI spec
        """
        try:
            spec = json.loads(spec_content)
            parser = OpenAPIParser(spec)
            endpoints = parser.get_endpoints()

            all_test_cases = []

            for endpoint in endpoints:
                path = endpoint["path"]
                method = endpoint["method"]
                details = endpoint["details"]

                # Get endpoint-specific spec
                endpoint_spec = {
                    "path": path,
                    "method": method,
                    "parameters": details.get("parameters", []),
                    "requestBody": details.get("requestBody", {}),
                    "responses": details.get("responses", {}),
                    "security": details.get("security", []),
                    "description": details.get("description", "")
                }

                # Generate tests using AI
                test_cases = self.ai_service.generate_test_cases(
                    endpoint_spec,
                    path,
                    method,
                    include_edge_cases
                )

                all_test_cases.extend(test_cases)

            return all_test_cases

        except Exception as e:
            print(f"Error generating tests: {str(e)}")
            return []
