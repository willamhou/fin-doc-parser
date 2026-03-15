"""Basic usage — parse a financial document in 3 lines."""

from findocparser import parse

# Parse a financial statement (PDF or image)
# Requires: DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable
result = parse("资产负债表2024.pdf")
print(f"Document type: {result['doc_type']}")
print(f"Total assets: {result['data']['balance_sheet']['total_assets']}")
