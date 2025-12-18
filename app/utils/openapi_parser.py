import json
from typing import Dict, Any, List


class OpenAPIParser:
    """Parse OpenAPI/Swagger specifications"""

    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec

    def get_endpoints(self) -> List[Dict[str, Any]]:
        """Extract all endpoints from the spec"""
        endpoints = []
        paths = self.spec.get("paths", {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "details": details
                    })

        return endpoints

    def get_endpoint_details(self, path: str, method: str) -> Dict[str, Any]:
        """Get details for a specific endpoint"""
        try:
            return self.spec["paths"][path][method.lower()]
        except KeyError:
            return {}

    def get_base_url(self) -> str:
        """Extract base URL from spec"""
        servers = self.spec.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        return ""
