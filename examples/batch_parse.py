"""Batch parsing — process multiple documents concurrently."""

import asyncio

from findocparser import parse_async


async def batch_parse(file_paths: list[str], llm_provider: str = "deepseek"):
    """Parse multiple documents concurrently."""
    tasks = [parse_async(fp, llm_provider=llm_provider) for fp in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for fp, result in zip(file_paths, results, strict=False):
        if isinstance(result, Exception):
            print(f"  FAILED {fp}: {result}")
        else:
            print(f"  OK {fp}: doc_type={result['doc_type']}")

    return [r for r in results if not isinstance(r, Exception)]


# Example usage:
# asyncio.run(batch_parse([
#     "资产负债表2024.pdf",
#     "银行流水_2024.pdf",
#     "营业执照.jpg",
#     "固定资产清单.xlsx",
# ]))
