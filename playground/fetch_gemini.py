import urllib.request
import urllib.error
import sys

# The target URL
url = "https://gemini.google.com/share/126c5742ffd0"
output_file = "C:/dev/erivlis/mappingtools/playground/fetched_gemini_content.html"

print(f"Attempting to fetch: {url}")

try:
    # Create a request with a User-Agent to avoid immediate 403s from some servers
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )

    with urllib.request.urlopen(req) as response:
        content = response.read().decode('utf-8')
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Success. Content saved to: {output_file}")
        print(f"Content length: {len(content)} characters")

except urllib.error.HTTPError as e:
    error_msg = f"HTTP Error: {e.code} - {e.reason}"
    print(error_msg)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"FAILED: {error_msg}")

except urllib.error.URLError as e:
    error_msg = f"URL Error: {e.reason}"
    print(error_msg)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"FAILED: {error_msg}")

except Exception as e:
    error_msg = f"General Error: {str(e)}"
    print(error_msg)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"FAILED: {error_msg}")
