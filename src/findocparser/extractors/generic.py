"""Generic extractor for unknown document types."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor


class GenericExtractor(BaseExtractor):
    """Fallback extractor for documents without a specialized extractor."""

    @property
    def doc_type(self) -> str:
        return "generic"

    @property
    def prompt_template(self) -> str:
        return """请分析以下金融文档内容，提取关键信息。

文档内容:
{content}

请以 JSON 格式返回以下字段:
{{
    "document_type": "检测到的文档类型",
    "title": "文档标题",
    "key_entities": ["关键实体列表"],
    "key_numbers": {{"指标名": 数值}},
    "summary": "文档摘要 (100字以内)",
    "extraction_confidence": 0.0-1.0
}}"""
