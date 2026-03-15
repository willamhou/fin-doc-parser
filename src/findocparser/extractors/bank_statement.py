"""Bank statement extractor."""

from __future__ import annotations

from findocparser.extractors.base import BaseExtractor
from findocparser.extractors.registry import register_extractor


@register_extractor
class BankStatementExtractor(BaseExtractor):
    """Extract structured transaction data from bank statements."""

    @property
    def doc_type(self) -> str:
        return "bank_statement"

    @property
    def prompt_template(self) -> str:
        return """请从以下银行流水中提取交易记录。

文档内容:
{content}

请以 JSON 格式返回:
{{
    "account_name": "账户名称",
    "account_number": "账号",
    "bank_name": "银行名称",
    "period_start": "流水开始日期",
    "period_end": "流水结束日期",
    "opening_balance": null,
    "closing_balance": null,
    "transactions": [
        {{
            "date": "交易日期 (YYYY-MM-DD)",
            "description": "摘要",
            "counterparty": "对手方",
            "amount": 金额(正数为收入负数为支出),
            "balance": 余额,
            "type": "credit | debit"
        }}
    ]
}}

注意: 最多提取前 200 条交易记录。金额为数值类型，不要带单位。"""
