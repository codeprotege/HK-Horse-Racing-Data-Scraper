import requests
from bs4 import BeautifulSoup
import string
import re
import json

def fetch_all_horse_ids():
    """
    Fetches all horse IDs from the HKJC website by iterating through the alphabetical index.

    Returns:
        list: A list of all unique horse IDs.
    """
    base_url = "https://racing.hkjc.com/racing/information/english/Horse/SelectHorsebyChar.aspx?ordertype="
    horse_ids = set()

    for letter in string.ascii_uppercase:
        url = base_url + letter
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page for letter {letter}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links in the main content that go to a horse's page
        horse_links = soup.select('div.commContent a[href*="Horse.aspx?HorseId="]')

        for link in horse_links:
            href = link.get('href')
            match = re.search(r'HorseId=([^&]+)', href)
            if match:
                horse_ids.add(match.group(1))

    return list(horse_ids)

if __name__ == '__main__':
    print("Fetching all horse IDs... This may take a moment.")
    ids = fetch_all_horse_ids()

    if ids:
        # Format for JSON output as requested
        output_data = [{"id": horse_id} for horse_id in ids]
        with open('horses.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully fetched and saved {len(ids)} horse IDs to horses.json")
    else:
        print("No horse IDs were fetched.")
