"""Governance configuration utilities for OpenAPI Generator."""

from typing import Dict, Any, List, Optional
import json
import yaml
from pathlib import Path
from .generator import OpenAPIGenerator


def load_governance_config(config_path: str) -> Dict[str, Any]:
    """Load governance configuration from JSON or YAML file.
    
    Args:
        config_path: Path to governance config file
        
    Returns:
        Dictionary with governance settings
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Governance config file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        if config_file.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(f) or {}
        else:
            return json.load(f)


def create_default_security_schemes() -> Dict[str, Any]:
    """Create default security schemes (JWT, API Key, OAuth2).
    
    Returns:
        Dictionary of security schemes
    """
    return {
        "BearerAuth": OpenAPIGenerator.create_jwt_security_scheme(),
        "ApiKeyAuth": OpenAPIGenerator.create_api_key_security_scheme(),
        "OAuth2": OpenAPIGenerator.create_oauth2_security_scheme(
            authorization_url="https://auth.example.com/oauth/authorize",
            token_url="https://auth.example.com/oauth/token",
            scopes={
                "read": "Read access",
                "write": "Write access"
            }
        )
    }


def create_default_mandatory_fields() -> List[Dict[str, Any]]:
    """Create default mandatory fields (traceId, timestamp, userId).
    
    Returns:
        List of mandatory field definitions
    """
    return [
        {
            "name": "traceId",
            "schema": {
                "type": "string",
                "format": "uuid",
                "description": "Unique trace identifier for request tracking"
            },
            "required": True,
            "apply_to": "both"  # 'request', 'response', or 'both'
        },
        {
            "name": "timestamp",
            "schema": {
                "type": "string",
                "format": "date-time",
                "description": "Request/response timestamp"
            },
            "required": True,
            "apply_to": "both"
        },
        {
            "name": "userId",
            "schema": {
                "type": "string",
                "description": "User identifier"
            },
            "required": False,
            "apply_to": "request"  # Only in requests
        }
    ]


def create_default_extensions() -> Dict[str, Any]:
    """Create default OpenAPI extensions.
    
    Returns:
        Dictionary of extension fields
    """
    return {
        "x-company-metadata": {
            "team": "Platform Team",
            "cost-center": "Engineering",
            "compliance": ["GDPR", "SOC2"]
        },
        "x-api-version": "1.0.0",
        "x-deprecated": False
    }

