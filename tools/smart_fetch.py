# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anyio"
#     "playwright",
#     "beautifulsoup4",
#     "html2text",
# ]
# ///

"""
Smart Fetch Tool
================

A robust utility to fetch dynamic web content (JavaScript-rendered) and convert it to clean Markdown.
It uses Playwright to render the page and html2text to format the output.

Prerequisites
-------------
Before running this script for the first time, you must install the Playwright browser binaries.
Use `uvx` to do this cleanly:

    $ uvx playwright install chromium

Usage
-----
Run the script using `uv run` to automatically handle the Python dependencies (playwright, bs4, html2text):

    $ uv run tools/smart_fetch.py <URL> <OUTPUT_FILE>

Example:
    $ uv run tools/smart_fetch.py "https://gemini.google.com/share/126c5742ffd0" "playground/gemini_chat_126c5742ffd0.md"

Features
--------
*   **Dynamic Rendering:** Handles Client-Side Rendering (CSR) apps like Gemini, React, Vue.
*   **Network Idle Wait:** Waits for network activity to settle to ensure content is loaded.
*   **Markdown Conversion:** Converts HTML to readable Markdown, stripping unnecessary links/images.
*   **Ephemeral Environment:** Uses PEP 723 inline metadata for zero-config execution with `uv`.
"""

import asyncio
import os
import sys

import anyio
import html2text
from playwright.async_api import async_playwright


async def fetch_and_convert(url, output_file):
    print(f"🚀 Launching browser to fetch: {url}")

    async with async_playwright() as p:
        # Launch browser (headless)
        try:
            browser = await p.chromium.launch()
        except Exception as e:
            print(f"❌ Error launching browser: {e}")
            print("💡 Hint: Did you run 'uvx playwright install chromium'?")
            sys.exit(1)

        page = await browser.new_page()

        # Go to URL and wait for network idle to ensure JS loads
        print("⏳ Loading page...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)  # 60s timeout
        except Exception as e:
            print(f"⚠️ Warning: Page load timed out or failed: {e}")
            print("   Attempting to proceed with partial content...")

        # Get the full HTML content
        html_content = await page.content()
        print("✅ Page loaded.")

        await browser.close()

    # Convert to Markdown
    print("📝 Converting to Markdown...")
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    converter.body_width = 0  # No wrapping
    markdown_content = converter.handle(html_content)

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save to file
    async with await anyio.open_file(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"💾 Saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: uv run tools/smart_fetch.py <URL> <OUTPUT_FILE>")
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2]

    asyncio.run(fetch_and_convert(url, output_file))
