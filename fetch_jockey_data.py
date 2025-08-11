import requests
from bs4 import BeautifulSoup
import json
import argparse
import re

def clean_text(text):
    """Removes extra whitespace and newlines from a string."""
    return ' '.join(text.split())

def fetch_jockey_data(jockey_id):
    """
    Fetches data for a specific jockey from the Hong Kong Jockey Club website.

    Args:
        jockey_id (str): The ID of the jockey (e.g., "FEL").

    Returns:
        dict: A dictionary containing the jockey's data.
    """
    url = f"https://racing.hkjc.com/racing/information/English/Jockey/JockeyProfile.aspx?JockeyId={jockey_id}&Season=Current"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    jockey_data = {"id": jockey_id}

    profile_div = soup.find('div', class_='jockeyProfile')
    if not profile_div:
        print("Could not find jockey profile data.")
        return None

    # Extract Name from the h1 tag inside the profile div
    name_td = profile_div.find('td', class_='subsubheader')
    if name_td:
        jockey_data['name'] = clean_text(name_td.text)
    else: # Fallback for different structure
        name_h1 = profile_div.find('h1')
        if name_h1:
            jockey_data['name'] = clean_text(name_h1.text)


    # The data is in a table with a messy structure.
    # We will find the labels and then get the next piece of text.
    # This is very fragile, but it's the best we can do with this HTML

    # Find all bold tags, which are used as labels
    bold_tags = profile_div.find_all('b')
    for tag in bold_tags:
        key = clean_text(tag.text).lower().replace(':', '').replace(' ', '_')
        # The value is the text that follows the bold tag until the next bold tag
        value = ''
        sibling = tag.next_sibling
        while sibling and sibling.name != 'b':
            if hasattr(sibling, 'text'):
                value += sibling.text
            else:
                value += str(sibling)
            sibling = sibling.next_sibling
        jockey_data[key] = clean_text(value)


    # Extract current season stats
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
        jockey_data['current_season_stats'] = stats


    return jockey_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch jockey data from the HKJC website.')
    parser.add_argument('jockey_id', type=str, help='The ID of the jockey (e.g., "FEL").')

    args = parser.parse_args()

    data = fetch_jockey_data(args.jockey_id)

    if data:
        print(json.dumps(data, indent=4))
