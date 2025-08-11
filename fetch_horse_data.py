import requests
from bs4 import BeautifulSoup
import json
import argparse
import re

def clean_text(text):
    """Removes extra whitespace and newlines from a string."""
    return ' '.join(text.split())

def fetch_horse_data(horse_id):
    """
    Fetches data for a specific horse from the Hong Kong Jockey Club website.

    Args:
        horse_id (str): The ID of the horse (e.g., "H108").

    Returns:
        dict: A dictionary containing the horse's data.
    """
    url = f"https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId={horse_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    horse_data = {"id": horse_id}

    # Extract horse name and code
    name_span = soup.find('span', class_='title_text')
    if name_span:
        horse_data['name'] = clean_text(name_span.text)

    # Extract basic info from the main table
    profile_table = soup.find('table', class_='horseProfile')
    if profile_table:
        # A more robust way to parse this messy table
        # Find all text nodes and look for our keys
        all_text = profile_table.find_all(string=True)
        for i, text in enumerate(all_text):
            clean = clean_text(text)
            if clean == "Country of Origin / Age":
                horse_data['country_of_origin_age'] = clean_text(all_text[i+2])
            if clean == "Colour / Sex":
                horse_data['colour_sex'] = clean_text(all_text[i+2])
            if clean == "Import Type":
                horse_data['import_type'] = clean_text(all_text[i+2])
            if clean == "Season Stakes*":
                horse_data['season_stakes'] = clean_text(all_text[i+2])
            if clean == "Total Stakes*":
                horse_data['total_stakes'] = clean_text(all_text[i+2])
            if clean == "No. of 1-2-3-Starts*":
                horse_data['starts'] = clean_text(all_text[i+2])
            if clean == "Trainer":
                horse_data['trainer'] = clean_text(all_text[i+2])
            if clean == "Owner":
                horse_data['owner'] = clean_text(all_text[i+2])
            if clean == "Current Rating":
                horse_data['current_rating'] = clean_text(all_text[i+2])
            if clean == "Sire":
                 horse_data['sire'] = clean_text(all_text[i+2])
            if clean == "Dam":
                horse_data['dam'] = clean_text(all_text[i+2])
            if clean == "Dam's Sire":
                horse_data['dams_sire'] = clean_text(all_text[i+2])

    # Extract past performance table
    performance_table = soup.find('table', class_='bigborder')
    if performance_table:
        headers = [clean_text(td.text) for td in performance_table.find_all('td', class_='hsubheader')]
        past_races = []
        for row in performance_table.find_all('tr'):
            # Skip header and season rows
            if row.find('td', class_='hsubheader') or row.find('td', class_='htable_bold_text'):
                continue

            cols = row.find_all('td')
            if len(cols) == len(headers):
                race_record = {}
                for i, header in enumerate(headers):
                    race_record[header] = clean_text(cols[i].text)
                past_races.append(race_record)
        horse_data['past_races'] = past_races

    return horse_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch horse data from the HKJC website.')
    parser.add_argument('horse_id', type=str, help='The ID of the horse (e.g., "HK_2022_H108").')

    args = parser.parse_args()

    data = fetch_horse_data(args.horse_id)

    if data:
        print(json.dumps(data, indent=4))
