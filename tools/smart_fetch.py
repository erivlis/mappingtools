# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anyio",
#     "playwright",
#     "beautifulsoup4",
#     "html2text",
#     "rich",
# ]
# ///

"""
Smart Fetch Tool
================

A robust utility to fetch dynamic web content (JavaScript-rendered) and convert it to clean Markdown.
It uses Playwright to render the page and html2text to format the output.

Prerequisites
-------------
No installation of Playwright binaries is strictly required. This script is configured
to use your local system's installation of Google Chrome or Microsoft Edge.

Usage
-----
Run the script using `uv run` to automatically handle the Python dependencies:

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
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme

# Set up Rich console with a custom theme for semantic logging
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
})
console = Console(theme=custom_theme)


async def fetch_and_convert(url: str, output_file: str):
    console.print(Panel(f"Target: [bold]{url}[/bold]\nOutput: [bold]{output_file}[/bold]", title="🚀 Smart Fetch Initialized", expand=False))

    async with async_playwright() as p:
        # Launch browser (headless) using the local system Chrome/Edge installation.
        # 'channel="chrome"' tells playwright to look for the system Chrome.
        # Alternatively, 'channel="msedge"' works on Windows.
        try:
            with console.status("[info]Launching local Chrome browser...", spinner="dots"):
                browser = await p.chromium.launch(channel="chrome")
        except Exception as e:
            console.print(f"[error]❌ Error launching local Chrome:[/error] {e}")
            console.print("[warning]💡 Hint: Ensure Google Chrome is installed on your system.[/warning]")
            console.print("[info]If Chrome is missing, you can install the Playwright binaries via: uvx playwright install chromium[/info]")
            sys.exit(1)

        page = await browser.new_page()

        # Go to URL and wait for network idle to ensure JS loads
        with console.status(f"[info]Loading page and waiting for network idle...[/info]", spinner="bouncingBar"):
            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)  # 60s timeout
                console.print("[success]✅ Page loaded successfully.[/success]")
            except Exception as e:
                console.print(f"[warning]⚠️ Warning: Page load timed out or failed: {e}[/warning]")
                console.print("[info]Attempting to proceed with partial content...[/info]")

        # Get the full HTML content
        with console.status("[info]Extracting HTML content...[/info]"):
            html_content = await page.content()

        await browser.close()

    # Convert to Markdown
    with console.status("[info]📝 Converting HTML to Markdown...[/info]"):
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.body_width = 0  # No wrapping
        markdown_content = converter.handle(html_content)

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save to file
    with console.status("[info]💾 Writing to disk...[/info]"):
        async with await anyio.open_file(output_file, "w", encoding="utf-8") as f:
            await f.write(markdown_content)

    console.print(f"[success]🎉 Done! Saved to: {output_file}[/success]")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        console.print("[error]Usage:[/error] uv run tools/smart_fetch.py <URL> <OUTPUT_FILE>")
        sys.exit(1)

    target_url = sys.argv[1]
    target_output = sys.argv[2]

    asyncio.run(fetch_and_convert(target_url, target_output))
