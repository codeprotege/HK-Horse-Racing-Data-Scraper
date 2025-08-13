import re
import sys
import requests

def get_horse_name(horse_id):
    """
    Scrapes the Chinese name of a horse from the HKJC website.

    Args:
        horse_id: The ID of the horse (e.g., HK_2022_H108).

    Returns:
        The Chinese name of the horse as a string, or None if not found.
    """
    url = f"https://racing.hkjc.com/racing/information/Chinese/Horse/Horse.aspx?HorseId={horse_id}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html_content = response.text

        # The name and ID are together inside the span: <span class="title_text">NAME (ID)</span>
        match = re.search(r'<span class="title_text">([^<]+)</span>', html_content)
        if match:
            full_text = match.group(1).strip()
            # Remove the ID part from the end of the string.
            # The ID is in the format (H108)
            horse_name = re.sub(r'\s*\([^\)]+\)$', '', full_text).strip()
            return horse_name

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the web request: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

    return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scrape_horse_name.py <horse_id>", file=sys.stderr)
        sys.exit(1)

    horse_id_input = sys.argv[1]
    horse_name = get_horse_name(horse_id_input)

    if horse_name:
        print(horse_name)
    else:
        print(f"ERROR: Could not find the name for horse ID: {horse_id_input}", file=sys.stderr)
        sys.exit(1)
