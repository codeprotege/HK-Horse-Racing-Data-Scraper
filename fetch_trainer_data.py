import requests
from bs4 import BeautifulSoup
import json
import argparse
import re

def clean_text(text):
    """Removes extra whitespace and newlines from a string."""
    return ' '.join(text.split())

def fetch_trainer_data(trainer_id, season="Current"):
    """
    Fetches data for a specific trainer from the Hong Kong Jockey Club website.

    Args:
        trainer_id (str): The ID of the trainer (e.g., "YTP").
        season (str): The season to fetch data for ("Current" or "Previous").

    Returns:
        dict: A dictionary containing the trainer's data.
    """
    url = f"https://racing.hkjc.com/racing/information/English/Trainers/TrainerProfile.aspx?TrainerId={trainer_id}&Season={season}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    trainer_data = {"id": trainer_id, "season": season}

    profile_div = soup.find('div', class_='trainerProfile')
    if not profile_div:
        # The class name is different on some pages
        profile_div = soup.find('div', class_='jockeyProfile') # Seems to be a copy-paste error on their side

    if not profile_div:
        print("Could not find trainer profile data.")
        return None

    # Extract Name
    name_strong = profile_div.find('strong')
    if name_strong:
        trainer_data['name'] = clean_text(name_strong.text)

    # Extract other details from the text
    bold_tags = profile_div.find_all('b')
    for tag in bold_tags:
        # Skip the name tag as we've already processed it
        if tag.find_parent('strong'):
            continue

        key = clean_text(tag.text).lower().replace(':', '').replace(' ', '_')
        value = ''
        sibling = tag.next_sibling
        while sibling:
            if sibling.name == 'b' or (hasattr(sibling, 'name') and sibling.name == 'br'):
                 break
            if hasattr(sibling, 'text'):
                value += sibling.text
            else:
                value += str(sibling)
            sibling = sibling.next_sibling
        trainer_data[key] = clean_text(value)

    # Extract season stats
    season_stats_table = profile_div.find('table', class_='table_bd')
    if season_stats_table:
        stats = {}
        rows = season_stats_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            for i in range(0, len(cells), 2):
                if i+1 < len(cells):
                    key = clean_text(cells[i].text).replace(':', '').lower().replace(' ', '_')
                    value = clean_text(cells[i+1].text).replace(':', '').strip()
                    if key and value:
                        stats[key] = value
        trainer_data['season_stats'] = stats

    return trainer_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch trainer data from the HKJC website.')
    parser.add_argument('trainer_id', type=str, help='The ID of the trainer (e.g., "YTP").')
    parser.add_argument('--season', type=str, default='Current', help='The season ("Current" or "Previous").')

    args = parser.parse_args()

    data = fetch_trainer_data(args.trainer_id, args.season)

    if data:
        print(json.dumps(data, indent=4))
