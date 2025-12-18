import ollama
import os
import json
from typing import List, Dict, Any


class AIService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(host=self.base_url)

    def generate_test_cases(self, openapi_spec: Dict[str, Any], endpoint: str,
                            method: str, include_edge_cases: bool = True) -> \
            List[Dict[str, Any]]:
        """
        Use Ollama (local LLM) to generate comprehensive test cases for an API endpoint
        """

        prompt = f"""[INST] <<SYS>>
        You are an API testing expert. Generate 2-3 test cases as a JSON array.
        <</SYS>>

        Endpoint: {method} {endpoint}
        OpenAPI Spec:
        {json.dumps(openapi_spec, indent=2)}

        Generate JSON array with 2-3 test cases. Each test case object should have: name, method, endpoint, headers, body, expected_status, expected_response, assertions.

        Return ONLY the JSON array. No explanations.
        [/INST]

        [
          {{"name": "Test 1", "method": "{method}", "endpoint": "{endpoint}", ...}},
          ...
        ]"""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'num_predict': 4000  # Increased from 2000 to 4000
                }
            )

            response_text = response['message']['content']
            print(
                f"DEBUG: Raw AI response: {response_text[:500]}...")  # For debugging

            # Clean up response if it has markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[
                    0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[
                    0].strip()

            # Find JSON array in response
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1

            if start_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]

            test_cases = json.loads(response_text)

            # Ensure it's a list
            if not isinstance(test_cases, list):
                test_cases = [test_cases]

            return test_cases

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Response text: {response_text}")

            # Try to fix common JSON issues
            try:
                # Try to complete truncated JSON
                if response_text.endswith(',') or not response_text.endswith(
                        ']'):
                    # Try to close the array
                    response_text = response_text.strip()
                    if response_text.endswith(','):
                        response_text = response_text[:-1]
                    if not response_text.endswith(']'):
                        response_text += ']'
                    test_cases = json.loads(response_text)
                    return test_cases
            except:
                pass

            return []
        except Exception as e:
            print(f"Error generating test cases: {str(e)}")
            return []

    def analyze_test_results(self, results: List[Dict[str, Any]]) -> Dict[
        str, Any]:
        """
        Use Ollama to analyze test execution results and provide insights
        """

        prompt = f"""You are an expert QA engineer analyzing API test results. 

Test Results Summary:
Total Tests: {len(results)}
Passed: {sum(1 for r in results if r.get('status') == 'passed')}
Failed: {sum(1 for r in results if r.get('status') == 'failed')}

Detailed Results:
{json.dumps(results[:10], indent=2)}  # Limit to first 10 for context

Provide analysis including:
1. Overall assessment of API quality
2. Critical issues found (if any)
3. Patterns in failures
4. Recommendations for improvement
5. Areas with good coverage
6. Areas needing more test coverage

IMPORTANT: Return ONLY a valid JSON object (not an array). No explanations, no markdown, no code blocks.

Required JSON structure:
{{
  "overall_quality_score": 85,
  "critical_issues": ["issue1", "issue2"],
  "failure_patterns": ["pattern1"],
  "recommendations": ["rec1", "rec2"],
  "well_covered_areas": ["area1"],
  "coverage_gaps": ["gap1"],
  "summary": "Brief summary in 2-3 sentences"
}}
"""

        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.7,
                    'num_predict': 1000
                }
            )

            response_text = response['message']['content']

            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[
                    0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[
                    0].strip()

            # Find JSON object in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx]

            analysis = json.loads(response_text)

            # Validate required keys
            required_keys = [
                'overall_quality_score', 'critical_issues', 'failure_patterns',
                'recommendations', 'well_covered_areas', 'coverage_gaps',
                'summary'
            ]

            for key in required_keys:
                if key not in analysis:
                    if key == 'overall_quality_score':
                        analysis[key] = 75
                    elif key == 'summary':
                        analysis[key] = "Analysis completed"
                    else:
                        analysis[key] = []

            return analysis


        except Exception as e:

            print(f"Error analyzing results: {str(e)}")

            return {

                "overall_quality_score": 0,

                "critical_issues": [],
                # Changed from ["Error performing analysis"]

                "failure_patterns": [],

                "recommendations": ["Check if tests were executed properly"],

                "well_covered_areas": [],

                "coverage_gaps": ["Unable to analyze - check test execution"],

                "summary": "Analysis failed due to an error"

            }


def _safe_parse_json(self, text: str) -> List[Dict[str, Any]]:
    """Safely parse JSON, trying multiple strategies if needed"""
    strategies = [
        # Strategy 1: Direct parse
        lambda t: json.loads(t),

        # Strategy 2: Extract JSON from markdown
        lambda t: json.loads(t.split("```json")[1].split("```")[0].strip()),

        # Strategy 3: Extract JSON array between [ and ]
        lambda t: json.loads(t[t.find('['):t.rfind(']') + 1]),

        # Strategy 4: Fix common issues and parse
        lambda t: json.loads(self._fix_json_issues(t))
    ]

    for strategy in strategies:
        try:
            return strategy(text)
        except:
            continue

    return []


def _fix_json_issues(self, text: str) -> str:
    """Fix common JSON issues"""
    # Remove any text before [
    if '[' in text:
        text = text[text.find('['):]

    # Ensure it ends with ]
    if not text.endswith(']'):
        # Find the last complete object
        brackets = 0
        for i, char in enumerate(text):
            if char == '{':
                brackets += 1
            elif char == '}':
                brackets -= 1
                if brackets == 0 and i > len(text) - 10:
                    # Close the array
                    text = text[:i + 1] + ']'
                    break

    # Fix trailing commas
    text = text.replace(',]', ']').replace(',}', '}')

    return text
