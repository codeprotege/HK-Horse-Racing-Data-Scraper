import requests
from bs4 import BeautifulSoup
import string
import re

def scrape_horse_data():
    """
    Scrapes horse names and IDs from the HKJC website.
    """
    base_url = "https://racing.hkjc.com/racing/information/english/Horse/SelectHorsebyChar.aspx?ordertype="

    for letter in string.ascii_uppercase:
        url = base_url + letter
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links that match the horse details page pattern
            horse_links = soup.find_all('a', href=re.compile(r'Horse\.aspx\?HorseId='))

            for link in horse_links:
                horse_name_full = link.text.strip()
                # Clean the horse name by removing the parenthetical part, e.g. (V355)
                horse_name = re.sub(r'\s*\([^)]*\)$', '', horse_name_full).strip()

                # The horse ID is in the href attribute
                horse_id_match = re.search(r'HorseId=([^&]+)', link['href'])
                if horse_id_match and horse_name:
                    horse_id = horse_id_match.group(1)
                    print(f"{horse_id},{horse_name}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching page for letter {letter}: {e}")

if __name__ == "__main__":
    scrape_horse_data()
