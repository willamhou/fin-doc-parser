"""Tests for LLM client — OpenAIClient and protocol compliance."""

from __future__ import annotations

import json

import pytest

from findocparser.llm.base import LLMClient
from findocparser.llm.openai_client import OpenAIClient


class TestOpenAIClientInit:
    """Test OpenAIClient construction and config resolution."""

    def test_requires_api_key(self):
        """Should raise ValueError when no API key is available."""
        with pytest.raises(ValueError, match="API key not found"):
            OpenAIClient(provider="openai")

    def test_accepts_explicit_api_key(self):
        client = OpenAIClient(provider="openai", api_key="test-key")
        assert client.api_key == "test-key"
        assert client.model == "gpt-4o-mini"
        assert "openai.com" in client.base_url

    def test_deepseek_defaults(self):
        client = OpenAIClient(provider="deepseek", api_key="test-key")
        assert client.model == "deepseek-chat"
        assert "deepseek.com" in client.base_url

    def test_custom_overrides(self):
        client = OpenAIClient(
            provider="openai",
            api_key="k",
            base_url="http://localhost:11434/v1",
            model="qwen2.5:14b",
        )
        assert client.base_url == "http://localhost:11434/v1"
        assert client.model == "qwen2.5:14b"

    def test_env_key_resolution(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "env-key-123")
        client = OpenAIClient(provider="deepseek")
        assert client.api_key == "env-key-123"


class TestParseJson:
    """Test JSON extraction from LLM response text."""

    def test_direct_json(self):
        text = '{"total_assets": 100}'
        assert OpenAIClient._parse_json(text) == {"total_assets": 100}

    def test_markdown_code_block(self):
        text = 'Here is the result:\n```json\n{"total_assets": 100}\n```'
        assert OpenAIClient._parse_json(text) == {"total_assets": 100}

    def test_embedded_json(self):
        text = 'The extraction result is {"total_assets": 100} done.'
        assert OpenAIClient._parse_json(text) == {"total_assets": 100}

    def test_fallback_on_invalid(self):
        text = "no json here at all"
        result = OpenAIClient._parse_json(text)
        assert "parse_error" in result
        assert result["raw_response"] == text


class TestProtocolCompliance:
    """Verify MockLLMClient and OpenAIClient satisfy LLMClient protocol."""

    def test_openai_client_is_llm_client(self):
        client = OpenAIClient(provider="openai", api_key="test")
        assert isinstance(client, LLMClient)

    def test_mock_client_is_llm_client(self, mock_llm):
        client = mock_llm()
        assert isinstance(client, LLMClient)


class TestLLMFactory:
    """Test get_llm_client factory."""

    def test_create_deepseek(self):
        from findocparser.llm.factory import get_llm_client

        client = get_llm_client("deepseek", api_key="test")
        assert isinstance(client, OpenAIClient)
        assert client.model == "deepseek-chat"

    def test_create_openai(self):
        from findocparser.llm.factory import get_llm_client

        client = get_llm_client("openai", api_key="test")
        assert isinstance(client, OpenAIClient)

    def test_unknown_provider_raises(self):
        from findocparser.llm.factory import get_llm_client

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm_client("gemini")

    def test_custom_kwargs_passthrough(self):
        from findocparser.llm.factory import get_llm_client

        client = get_llm_client(
            "openai",
            api_key="k",
            base_url="http://localhost:11434/v1",
            model="llama3",
        )
        assert client.base_url == "http://localhost:11434/v1"
        assert client.model == "llama3"
