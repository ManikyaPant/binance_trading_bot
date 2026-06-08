"""Unit tests for bot.config."""

import os
import tempfile
import unittest
from unittest import mock

from bot.config import _load_dotenv


class TestLoadDotenv(unittest.TestCase):
    """Tests for the minimal .env file parser."""

    def test_loads_key_value_pairs(self):
        """Parses simple KEY=VALUE lines into os.environ."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False,
        ) as fh:
            fh.write("TEST_KEY_A=hello\n")
            fh.write("TEST_KEY_B=world\n")
            path = fh.name

        try:
            _load_dotenv(path)
            self.assertEqual(os.environ.get("TEST_KEY_A"), "hello")
            self.assertEqual(os.environ.get("TEST_KEY_B"), "world")
        finally:
            os.environ.pop("TEST_KEY_A", None)
            os.environ.pop("TEST_KEY_B", None)
            os.unlink(path)

    def test_skips_comments_and_blanks(self):
        """Lines starting with '#' and blank lines are ignored."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False,
        ) as fh:
            fh.write("# This is a comment\n")
            fh.write("\n")
            fh.write("TEST_KEY_C=value\n")
            path = fh.name

        try:
            _load_dotenv(path)
            self.assertEqual(os.environ.get("TEST_KEY_C"), "value")
        finally:
            os.environ.pop("TEST_KEY_C", None)
            os.unlink(path)

    def test_strips_quotes_from_values(self):
        """Double and single quotes around values are removed."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False,
        ) as fh:
            fh.write('TEST_KEY_D="quoted"\n')
            fh.write("TEST_KEY_E='single'\n")
            path = fh.name

        try:
            _load_dotenv(path)
            self.assertEqual(os.environ.get("TEST_KEY_D"), "quoted")
            self.assertEqual(os.environ.get("TEST_KEY_E"), "single")
        finally:
            os.environ.pop("TEST_KEY_D", None)
            os.environ.pop("TEST_KEY_E", None)
            os.unlink(path)

    def test_missing_file_is_silent(self):
        """A non-existent .env file does not raise."""
        _load_dotenv("/tmp/nonexistent_env_file_12345")


class TestLoadConfig(unittest.TestCase):
    """Tests for the load_config function."""

    @mock.patch("bot.config._load_dotenv")
    @mock.patch.dict(os.environ, {
        "BINANCE_API_KEY": "test_key_123",
        "BINANCE_API_SECRET": "test_secret_456",
    })
    def test_returns_credentials_from_env(self, mock_dotenv):
        """Returns a dict with api_key and api_secret from environment."""
        from bot.config import load_config
        config = load_config()
        self.assertEqual(config["api_key"], "test_key_123")
        self.assertEqual(config["api_secret"], "test_secret_456")

    @mock.patch("bot.config._load_dotenv")
    @mock.patch.dict(os.environ, {}, clear=True)
    def test_missing_vars_raises(self, mock_dotenv):
        """Raises EnvironmentError when both vars are missing."""
        from bot.config import load_config
        with self.assertRaises(EnvironmentError) as ctx:
            load_config()
        self.assertIn("BINANCE_API_KEY", str(ctx.exception))

    @mock.patch("bot.config._load_dotenv")
    @mock.patch.dict(os.environ, {
        "BINANCE_API_KEY": "key_only",
    }, clear=True)
    def test_missing_secret_raises(self, mock_dotenv):
        """Raises EnvironmentError when only API_SECRET is missing."""
        from bot.config import load_config
        with self.assertRaises(EnvironmentError) as ctx:
            load_config()
        self.assertIn("BINANCE_API_SECRET", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
