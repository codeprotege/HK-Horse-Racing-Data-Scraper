import requests
from bs4 import BeautifulSoup
import string
import re
import json

def find_all_horse_ids():
    """
    Finds all horse IDs by crawling the A-Z index on the HKJC website.
    """
    base_url = "https://racing.hkjc.com/racing/information/english/Horse/"
    all_horse_ids = set()

    # Iterate through letters A to Z
    for char_code in range(ord('A'), ord('Z') + 1):
        char = chr(char_code)
        index_url = f"{base_url}SelectHorsebyChar.aspx?ordertype={char}"

        try:
            print(f"Fetching horse index for letter: {char}")
            response = requests.get(index_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching index page for letter {char}: {e}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links that point to a horse's page
        # The links should contain 'Horse.aspx?HorseId='
        horse_links = soup.find_all('a', href=re.compile(r'Horse\.aspx\?HorseId='))

        if not horse_links:
            print(f"  No horse links found for letter {char}.")
            continue

        count = 0
        for link in horse_links:
            href = link.get('href')
            # Extract the HorseId from the href attribute
            match = re.search(r'HorseId=([^&]+)', href)
            if match:
                horse_id = match.group(1)
                if horse_id not in all_horse_ids:
                    all_horse_ids.add(horse_id)
                    count += 1

        print(f"  Found {count} new horse IDs for letter {char}.")

    return sorted(list(all_horse_ids))

if __name__ == "__main__":
    ids = find_all_horse_ids()
    if ids:
        print(f"\nFound a total of {len(ids)} unique horse IDs.")

        # Save the IDs to a text file
        with open("horse_ids.txt", "w") as f:
            for horse_id in ids:
                f.write(f"{horse_id}\n")
        print("Successfully saved all horse IDs to horse_ids.txt")

        # Also save as JSON for easier use in other scripts
        with open("horse_ids.json", "w") as f:
            json.dump(ids, f, indent=4)
        print("Successfully saved all horse IDs to horse_ids.json")

    else:
        print("\nCould not find any horse IDs.")
