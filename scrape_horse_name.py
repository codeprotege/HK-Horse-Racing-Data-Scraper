import re
import sys
import requests
import json

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

        match = re.search(r'<span class="title_text">([^<]+)</span>', html_content)
        if match:
            full_text = match.group(1).strip()
            horse_name = re.sub(r'\s*\([^\)]+\)$', '', full_text).strip()
            return horse_name

    except requests.exceptions.RequestException as e:
        # This will be handled in the main function
        return None
    except Exception as e:
        # This will be handled in the main function
        return None

    return None

def main():
    """
    Main function to handle command-line arguments, call the scraper,
    and print the output in JSON format.
    """
    if len(sys.argv) != 2:
        error_data = {
            "error": "Usage: python scrape_horse_name.py <horse_id>"
        }
        print(json.dumps(error_data, ensure_ascii=False, indent=2))
        sys.exit(1)

    horse_id_input = sys.argv[1]
    horse_name = get_horse_name(horse_id_input)

    if horse_name:
        output_data = {
            "horse_id": horse_id_input,
            "chinese_name": horse_name
        }
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        error_data = {
            "horse_id": horse_id_input,
            "error": f"Could not find the name for horse ID: {horse_id_input}"
        }
        print(json.dumps(error_data, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
