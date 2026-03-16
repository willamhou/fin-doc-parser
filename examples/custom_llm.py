"""Custom LLM endpoint — use Ollama, vLLM, or any OpenAI-compatible API."""

from findocparser import OpenAIClient, parse_async
from findocparser.extractors.registry import get_extractor
from findocparser.parsers.excel import parse_excel

# --- Option 1: Pass config through parse() (sync) ---

# result = parse(
#     "report.pdf",
#     llm_base_url="http://localhost:11434/v1",  # Ollama
#     llm_api_key="ollama",
#     llm_model="qwen2.5:14b",
# )
# print(result["data"])


# --- Option 2: Bring your own LLM client ---

client = OpenAIClient(
    provider="openai",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model="qwen2.5:14b",
)


async def main():
    # Use the client directly with an extractor
    content = parse_excel("固定资产清单.xlsx")
    extractor = get_extractor("fixed_asset")
    data = await extractor.extract(content, client)
    print(data)

    # Or pass it to parse_async()
    result = await parse_async("report.pdf", llm_client=client)
    print(result)


# asyncio.run(main())
