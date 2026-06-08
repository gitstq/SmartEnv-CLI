"""Core functionality for SmartEnv-CLI."""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class EnvVariable:
    """Represents an environment variable."""
    key: str
    value: str
    comment: str = ""
    is_sensitive: bool = False
    source: str = ""


@dataclass
class ProjectProfile:
    """Project type profile for smart detection."""
    name: str
    indicators: List[str]
    common_vars: Dict[str, str]
    sensitive_patterns: List[str]


# Predefined project profiles for smart detection
PROJECT_PROFILES = [
    ProjectProfile(
        name="django",
        indicators=["manage.py", "settings.py", "wsgi.py"],
        common_vars={
            "DEBUG": "True",
            "SECRET_KEY": "",
            "DATABASE_URL": "sqlite:///db.sqlite3",
            "ALLOWED_HOSTS": "*",
            "STATIC_URL": "/static/",
            "MEDIA_URL": "/media/",
        },
        sensitive_patterns=["SECRET_KEY", "PASSWORD", "API_KEY", "TOKEN"],
    ),
    ProjectProfile(
        name="flask",
        indicators=["app.py", "wsgi.py", "config.py"],
        common_vars={
            "FLASK_ENV": "development",
            "FLASK_DEBUG": "True",
            "SECRET_KEY": "",
            "DATABASE_URI": "sqlite:///app.db",
            "JWT_SECRET_KEY": "",
        },
        sensitive_patterns=["SECRET_KEY", "PASSWORD", "API_KEY", "TOKEN", "JWT"],
    ),
    ProjectProfile(
        name="fastapi",
        indicators=["main.py", "app/main.py", "api/"],
        common_vars={
            "APP_ENV": "development",
            "DEBUG": "True",
            "DATABASE_URL": "sqlite:///./app.db",
            "SECRET_KEY": "",
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        },
        sensitive_patterns=["SECRET_KEY", "PASSWORD", "API_KEY", "TOKEN"],
    ),
    ProjectProfile(
        name="node",
        indicators=["package.json", "server.js", "app.js"],
        common_vars={
            "NODE_ENV": "development",
            "PORT": "3000",
            "DATABASE_URL": "",
            "JWT_SECRET": "",
            "API_KEY": "",
        },
        sensitive_patterns=["SECRET", "PASSWORD", "API_KEY", "TOKEN", "PRIVATE_KEY"],
    ),
    ProjectProfile(
        name="react",
        indicators=["src/App.js", "src/App.tsx", "public/index.html"],
        common_vars={
            "REACT_APP_API_URL": "http://localhost:8000",
            "REACT_APP_ENV": "development",
            "PUBLIC_URL": "",
        },
        sensitive_patterns=["API_KEY", "SECRET", "TOKEN"],
    ),
    ProjectProfile(
        name="docker",
        indicators=["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        common_vars={
            "COMPOSE_PROJECT_NAME": "myapp",
            "DOCKER_REGISTRY": "",
            "DB_HOST": "db",
            "DB_PORT": "5432",
            "DB_NAME": "app",
            "DB_USER": "postgres",
            "DB_PASSWORD": "",
        },
        sensitive_patterns=["PASSWORD", "SECRET", "TOKEN", "KEY"],
    ),
    ProjectProfile(
        name="generic",
        indicators=[],
        common_vars={
            "APP_ENV": "development",
            "DEBUG": "True",
            "LOG_LEVEL": "INFO",
            "PORT": "8000",
            "HOST": "0.0.0.0",
        },
        sensitive_patterns=["PASSWORD", "SECRET", "TOKEN", "KEY", "PRIVATE"],
    ),
]


class EnvFileManager:
    """Manages .env file operations."""

    def __init__(self, env_path: str = ".env"):
        self.env_path = Path(env_path)
        self.variables: Dict[str, EnvVariable] = {}

    def detect_project_type(self, project_path: str = ".") -> ProjectProfile:
        """Detect project type based on file indicators."""
        project_path = Path(project_path)
        
        for profile in PROJECT_PROFILES:
            if profile.name == "generic":
                continue
            for indicator in profile.indicators:
                if (project_path / indicator).exists():
                    return profile
        
        return PROJECT_PROFILES[-1]  # Return generic profile

    def parse_env_file(self) -> Dict[str, EnvVariable]:
        """Parse .env file and return variables."""
        self.variables = {}
        
        if not self.env_path.exists():
            return self.variables

        with open(self.env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_comment = ""
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith("#"):
                if line.startswith("#"):
                    current_comment = line[1:].strip()
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # Detect sensitive variables
                is_sensitive = any(
                    pattern.lower() in key.lower() 
                    for pattern in ["password", "secret", "token", "key", "private", "auth"]
                )
                
                self.variables[key] = EnvVariable(
                    key=key,
                    value=value,
                    comment=current_comment,
                    is_sensitive=is_sensitive,
                    source=str(self.env_path),
                )
                current_comment = ""

        return self.variables

    def write_env_file(self, variables: Dict[str, EnvVariable], path: Optional[str] = None) -> None:
        """Write variables to .env file."""
        output_path = Path(path) if path else self.env_path
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# Auto-generated by SmartEnv-CLI\n")
            f.write(f"# Source: {output_path}\n\n")
            
            for key, var in variables.items():
                if var.comment:
                    f.write(f"# {var.comment}\n")
                if var.is_sensitive:
                    f.write(f"# ⚠️  SENSITIVE: {key}\n")
                f.write(f'{key}="{var.value}"\n\n')

    def generate_example(self, project_path: str = ".") -> Dict[str, EnvVariable]:
        """Generate .env.example from project detection."""
        profile = self.detect_project_type(project_path)
        example_vars = {}
        
        for key, default_value in profile.common_vars.items():
            is_sensitive = any(
                pattern.lower() in key.lower() 
                for pattern in profile.sensitive_patterns
            )
            
            example_vars[key] = EnvVariable(
                key=key,
                value="your_value_here" if is_sensitive else default_value,
                comment=f"Required for {profile.name}" if is_sensitive else f"Default: {default_value}",
                is_sensitive=is_sensitive,
            )
        
        # Also include existing variables from .env if present
        if self.env_path.exists():
            existing = self.parse_env_file()
            for key, var in existing.items():
                if key not in example_vars:
                    example_vars[key] = EnvVariable(
                        key=key,
                        value="your_value_here" if var.is_sensitive else var.value,
                        comment=var.comment,
                        is_sensitive=var.is_sensitive,
                    )
        
        return example_vars

    def compare_envs(self, other_env_path: str) -> Dict[str, Any]:
        """Compare current .env with another .env file."""
        other_manager = EnvFileManager(other_env_path)
        other_vars = other_manager.parse_env_file()
        current_vars = self.parse_env_file()
        
        result = {
            "missing_in_current": [],
            "missing_in_other": [],
            "different_values": [],
            "same_values": [],
        }
        
        for key in other_vars:
            if key not in current_vars:
                result["missing_in_current"].append(key)
            elif current_vars[key].value != other_vars[key].value:
                result["different_values"].append({
                    "key": key,
                    "current": current_vars[key].value,
                    "other": other_vars[key].value,
                })
            else:
                result["same_values"].append(key)
        
        for key in current_vars:
            if key not in other_vars:
                result["missing_in_other"].append(key)
        
        return result

    def validate(self) -> List[Dict[str, Any]]:
        """Validate .env file for common issues."""
        issues = []
        variables = self.parse_env_file()
        
        for key, var in variables.items():
            # Check for empty sensitive values
            if var.is_sensitive and not var.value:
                issues.append({
                    "type": "warning",
                    "key": key,
                    "message": f"Sensitive variable '{key}' has an empty value",
                })
            
            # Check for hardcoded secrets
            if var.is_sensitive and var.value and len(var.value) < 8:
                issues.append({
                    "type": "error",
                    "key": key,
                    "message": f"Potentially weak value for '{key}'",
                })
            
            # Check for spaces in keys
            if " " in key:
                issues.append({
                    "type": "error",
                    "key": key,
                    "message": f"Key '{key}' contains spaces",
                })
        
        return issues


class EnvSyncManager:
    """Manages synchronization between multiple environment files."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.environments = ["development", "staging", "production", "testing"]

    def get_env_files(self) -> List[Path]:
        """Discover all .env files in project."""
        env_files = []
        
        # Common env file patterns
        patterns = [
            ".env",
            ".env.local",
            ".env.example",
            ".env.template",
        ]
        
        for env in self.environments:
            patterns.extend([
                f".env.{env}",
                f".env.{env}.local",
            ])
        
        for pattern in patterns:
            path = self.base_path / pattern
            if path.exists():
                env_files.append(path)
        
        return env_files

    def sync_from_template(self, template_path: str = ".env.example") -> Dict[str, Any]:
        """Sync all env files from template."""
        template = EnvFileManager(template_path)
        template_vars = template.parse_env_file()
        
        results = {}
        for env_file in self.get_env_files():
            if env_file.name == template_path:
                continue
            
            manager = EnvFileManager(str(env_file))
            existing = manager.parse_env_file()
            
            # Add missing variables from template
            added = []
            for key, var in template_vars.items():
                if key not in existing:
                    existing[key] = EnvVariable(
                        key=key,
                        value="",
                        comment=var.comment,
                        is_sensitive=var.is_sensitive,
                    )
                    added.append(key)
            
            manager.write_env_file(existing)
            results[env_file.name] = {
                "added": added,
                "total_vars": len(existing),
            }
        
        return results


class EnvSecurityManager:
    """Manages security operations for environment variables."""

    def __init__(self, key_file: str = ".smartenv.key"):
        self.key_file = Path(key_file)
        self._key: Optional[bytes] = None

    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key."""
        from cryptography.fernet import Fernet
        
        if self._key is not None:
            return self._key
        
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                self._key = f.read()
        else:
            self._key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self._key)
            # Set restrictive permissions
            os.chmod(self.key_file, 0o600)
        
        return self._key

    def encrypt_value(self, value: str) -> str:
        """Encrypt a single value."""
        from cryptography.fernet import Fernet
        
        key = self._get_or_create_key()
        f = Fernet(key)
        encrypted = f.encrypt(value.encode())
        return f"ENC({encrypted.decode()})"

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a single value."""
        from cryptography.fernet import Fernet
        
        if not encrypted_value.startswith("ENC(") or not encrypted_value.endswith(")"):
            return encrypted_value
        
        key = self._get_or_create_key()
        f = Fernet(key)
        encrypted = encrypted_value[4:-1].encode()
        return f.decrypt(encrypted).decode()

    def encrypt_env_file(self, env_path: str = ".env", output_path: Optional[str] = None) -> List[str]:
        """Encrypt sensitive values in .env file."""
        manager = EnvFileManager(env_path)
        variables = manager.parse_env_file()
        
        encrypted_keys = []
        for key, var in variables.items():
            if var.is_sensitive and var.value and not var.value.startswith("ENC("):
                var.value = self.encrypt_value(var.value)
                encrypted_keys.append(key)
        
        output = output_path or env_path
        manager.write_env_file(variables, output)
        
        return encrypted_keys

    def decrypt_env_file(self, env_path: str = ".env", output_path: Optional[str] = None) -> List[str]:
        """Decrypt values in .env file."""
        manager = EnvFileManager(env_path)
        variables = manager.parse_env_file()
        
        decrypted_keys = []
        for key, var in variables.items():
            if var.value.startswith("ENC("):
                var.value = self.decrypt_value(var.value)
                decrypted_keys.append(key)
        
        output = output_path or env_path
        manager.write_env_file(variables, output)
        
        return decrypted_keys
