"""Tests for SmartEnv-CLI core functionality."""

import os
import tempfile
from pathlib import Path

import pytest

from smartenv.core import (
    EnvFileManager,
    EnvSyncManager,
    EnvSecurityManager,
    EnvVariable,
    PROJECT_PROFILES,
)


class TestEnvFileManager:
    """Test cases for EnvFileManager."""

    def test_parse_env_file(self):
        """Test parsing a valid .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# Database settings\n")
            f.write('DATABASE_URL="postgresql://localhost/db"\n')
            f.write("DEBUG=True\n")
            f.write("SECRET_KEY=mysecret\n")
            temp_path = f.name

        try:
            manager = EnvFileManager(temp_path)
            variables = manager.parse_env_file()

            assert "DATABASE_URL" in variables
            assert variables["DATABASE_URL"].value == "postgresql://localhost/db"
            assert variables["DATABASE_URL"].comment == "Database settings"
            assert not variables["DATABASE_URL"].is_sensitive

            assert "DEBUG" in variables
            assert variables["DEBUG"].value == "True"
            assert not variables["DEBUG"].is_sensitive

            assert "SECRET_KEY" in variables
            assert variables["SECRET_KEY"].is_sensitive
        finally:
            os.unlink(temp_path)

    def test_write_env_file(self):
        """Test writing variables to .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            temp_path = f.name

        try:
            manager = EnvFileManager(temp_path)
            variables = {
                "TEST_VAR": EnvVariable(key="TEST_VAR", value="test_value", comment="Test comment"),
                "SECRET": EnvVariable(key="SECRET", value="hidden", is_sensitive=True),
            }

            manager.write_env_file(variables)

            assert Path(temp_path).exists()
            content = Path(temp_path).read_text()
            assert 'TEST_VAR="test_value"' in content
            assert 'SECRET="hidden"' in content
            assert "SENSITIVE" in content
        finally:
            os.unlink(temp_path)

    def test_detect_project_type_django(self):
        """Test Django project detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Django indicator files
            (Path(tmpdir) / "manage.py").write_text("# Django manage.py")
            
            manager = EnvFileManager()
            profile = manager.detect_project_type(tmpdir)
            
            assert profile.name == "django"

    def test_detect_project_type_flask(self):
        """Test Flask project detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# Flask app")
            
            manager = EnvFileManager()
            profile = manager.detect_project_type(tmpdir)
            
            assert profile.name == "flask"

    def test_detect_project_type_generic(self):
        """Test generic project detection fallback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = EnvFileManager()
            profile = manager.detect_project_type(tmpdir)
            
            assert profile.name == "generic"

    def test_generate_example(self):
        """Test generating .env.example."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# Flask app")
            
            manager = EnvFileManager()
            example_vars = manager.generate_example(tmpdir)
            
            assert "FLASK_ENV" in example_vars
            assert "SECRET_KEY" in example_vars
            assert example_vars["SECRET_KEY"].is_sensitive

    def test_compare_envs(self):
        """Test comparing two .env files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f1:
            f1.write("VAR1=value1\n")
            f1.write("VAR2=value2\n")
            path1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f2:
            f2.write("VAR1=value1\n")
            f2.write("VAR3=value3\n")
            path2 = f2.name

        try:
            manager = EnvFileManager(path1)
            result = manager.compare_envs(path2)

            assert "VAR3" in result["missing_in_current"]
            assert "VAR2" in result["missing_in_other"]
            assert "VAR1" in result["same_values"]
        finally:
            os.unlink(path1)
            os.unlink(path2)

    def test_validate_empty_sensitive(self):
        """Test validation catches empty sensitive values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('SECRET_KEY=""\n')
            temp_path = f.name

        try:
            manager = EnvFileManager(temp_path)
            issues = manager.validate()

            assert len(issues) > 0
            assert any(i["key"] == "SECRET_KEY" for i in issues)
        finally:
            os.unlink(temp_path)

    def test_validate_weak_secret(self):
        """Test validation catches weak secrets."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('SECRET_KEY="abc"\n')
            temp_path = f.name

        try:
            manager = EnvFileManager(temp_path)
            issues = manager.validate()

            assert any(
                i["key"] == "SECRET_KEY" and "weak" in i["message"].lower()
                for i in issues
            )
        finally:
            os.unlink(temp_path)


class TestEnvSyncManager:
    """Test cases for EnvSyncManager."""

    def test_get_env_files(self):
        """Test discovering env files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".env").write_text("VAR1=value1\n")
            (Path(tmpdir) / ".env.development").write_text("VAR1=dev_value\n")
            
            sync_manager = EnvSyncManager(tmpdir)
            files = sync_manager.get_env_files()
            
            assert len(files) == 2

    def test_sync_from_template(self):
        """Test syncing env files from template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create template
            template_path = Path(tmpdir) / ".env.example"
            template_path.write_text("VAR1=default\nVAR2=default\n")
            
            # Create existing env file
            env_path = Path(tmpdir) / ".env.development"
            env_path.write_text("VAR1=dev\n")
            
            sync_manager = EnvSyncManager(tmpdir)
            results = sync_manager.sync_from_template(str(template_path))
            
            assert ".env.development" in results
            assert "VAR2" in results[".env.development"]["added"]


class TestEnvSecurityManager:
    """Test cases for EnvSecurityManager."""

    def test_encrypt_decrypt_value(self):
        """Test encrypting and decrypting a value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_file = Path(tmpdir) / ".smartenv.key"
            security = EnvSecurityManager(str(key_file))
            
            original = "my_secret_value"
            encrypted = security.encrypt_value(original)
            
            assert encrypted.startswith("ENC(")
            assert encrypted.endswith(")")
            
            decrypted = security.decrypt_value(encrypted)
            assert decrypted == original

    def test_encrypt_env_file(self):
        """Test encrypting sensitive values in env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text('SECRET_KEY="mysecret"\nDEBUG="True"\n')
            
            key_file = Path(tmpdir) / ".smartenv.key"
            security = EnvSecurityManager(str(key_file))
            
            encrypted_keys = security.encrypt_env_file(str(env_path))
            
            assert "SECRET_KEY" in encrypted_keys
            
            # Verify file was updated
            content = env_path.read_text()
            assert "ENC(" in content
            assert "DEBUG" in content

    def test_decrypt_env_file(self):
        """Test decrypting values in env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_path = Path(tmpdir) / ".env"
            env_path.write_text('SECRET_KEY="mysecret"\nDEBUG="True"\n')
            
            key_file = Path(tmpdir) / ".smartenv.key"
            security = EnvSecurityManager(str(key_file))
            
            # First encrypt
            security.encrypt_env_file(str(env_path))
            
            # Then decrypt
            decrypted_keys = security.decrypt_env_file(str(env_path))
            
            assert "SECRET_KEY" in decrypted_keys
            
            # Verify file was restored
            content = env_path.read_text()
            assert 'SECRET_KEY="mysecret"' in content


class TestProjectProfiles:
    """Test cases for project profiles."""

    def test_all_profiles_have_name(self):
        """Test all profiles have required attributes."""
        for profile in PROJECT_PROFILES:
            assert profile.name
            assert isinstance(profile.indicators, list)
            assert isinstance(profile.common_vars, dict)
            assert isinstance(profile.sensitive_patterns, list)

    def test_generic_profile_exists(self):
        """Test generic fallback profile exists."""
        profile_names = [p.name for p in PROJECT_PROFILES]
        assert "generic" in profile_names
