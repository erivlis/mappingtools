import json
import re
import sys

try:
    from bs4 import BeautifulSoup
    print("BeautifulSoup is available.")
except ImportError:
    print("BeautifulSoup is NOT available. Using regex fallback.")
    BeautifulSoup = None

input_file = "C:/dev/erivlis/mappingtools/playground/fetched_gemini_content.html"
output_file = "C:/dev/erivlis/mappingtools/playground/parsed_gemini_content.txt"

def extract_json_from_html(html_content):
    # Look for the specific WIZ_global_data pattern
    # window.WIZ_global_data = { ... };
    pattern = r'window\.WIZ_global_data\s*=\s*({.*?});'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        try:
            data = json.loads(json_str)
            return data
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return None
    return None

def extract_text_recursively(data, text_list):
    if isinstance(data, str):
        # Filter out short strings or obvious code/urls
        if len(data) > 50 and not data.startswith("http") and "{" not in data:
            text_list.append(data)
    elif isinstance(data, list):
        for item in data:
            extract_text_recursively(item, text_list)
    elif isinstance(data, dict):
        for key, value in data.items():
            extract_text_recursively(value, text_list)

try:
    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    data = extract_json_from_html(html_content)
    
    extracted_texts = []
    if data:
        print("Found WIZ_global_data. Extracting text...")
        extract_text_recursively(data, extracted_texts)
    else:
        print("Could not find or parse WIZ_global_data.")
        # Fallback: simple regex for long strings in the whole file
        print("Attempting fallback regex scan...")
        # Look for strings inside quotes that are reasonably long
        fallback_matches = re.findall(r'"([^"]{50,})"', html_content)
        for m in fallback_matches:
             if not m.startswith("http") and "{" not in m:
                 extracted_texts.append(m)

    # Write results
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("--- Extracted Text Candidates ---\n\n")
        for i, text in enumerate(extracted_texts):
            f.write(f"[{i}] {text}\n\n")
            
    print(f"Extraction complete. Found {len(extracted_texts)} candidates.")
    print(f"Saved to {output_file}")

except Exception as e:
    print(f"Error: {e}")
