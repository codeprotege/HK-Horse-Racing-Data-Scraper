import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_horse_data(horse_id):
    """
    Scrapes data for a given horse_id from the HKJC website.
    """
    url = f"https://racing.hkjc.com/racing/information/English/Horse/Horse.aspx?HorseId={horse_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    horse_data = {}

    # --- Extract Horse Name ---
    name_div = soup.find('div', class_='horse_title')
    if name_div:
        horse_data['name'] = name_div.get_text(strip=True).replace('\n', ' ').strip()
    elif soup.title:
        title_text = soup.title.string
        name_match = re.match(r'(.+?)\s*\(', title_text)
        if name_match:
            horse_data['name'] = name_match.group(1).strip()

    # --- Extract Basic Info ---
    body_text = soup.body.get_text('\n', strip=True)

    def extract_with_regex(pattern):
        match = re.search(pattern, body_text)
        if match:
            res = next((g for g in match.groups() if g), None)
            return res.strip().replace('\n', ' ') if res else None
        return None

    basic_info = {
        'Country of Origin / Age': extract_with_regex(r"Country of Origin / Age\s*:\s*(.*)"),
        'Colour / Sex': extract_with_regex(r"Colour / Sex\s*:\s*(.*)"),
        'Import Type': extract_with_regex(r"Import Type\s*:\s*(.*)"),
        'Season Stakes*': extract_with_regex(r"Season Stakes\*\s*:\s*(.*)"),
        'Total Stakes*': extract_with_regex(r"Total Stakes\*\s*:\s*(.*)"),
        'No. of 1-2-3-Starts*': extract_with_regex(r"No\. of 1-2-3-Starts\*\s*:\s*(.*)"),
        'Trainer': extract_with_regex(r"Trainer\s*:\s*(?:\[\w+\])?\s*(.*)"),
        'Owner': extract_with_regex(r"Owner\s*:\s*(?:\[.+?\])?\s*(.*)"),
        'Current Rating': extract_with_regex(r"Current Rating\s*:\s*(.*)"),
        'Start of Season Rating': extract_with_regex(r"Start of\s+Season Rating\s*:\s*(.*)"),
        'Sire': extract_with_regex(r"Sire\s*:\s*(?:\[\w+\])?\s*(.*)"),
        'Dam': extract_with_regex(r"Dam\s*:\s*(.*)"),
        "Dam's Sire": extract_with_regex(r"Dam's Sire\s*:\s*(.*)"),
    }
    horse_data['basic_info'] = {k: v for k, v in basic_info.items() if v}

    # --- Extract Race History ---
    race_history = []
    history_table = soup.find('table', class_='bigborder')

    if history_table:
        rows = history_table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 15 and cols[0].get_text(strip=True).isdigit():
                race = {
                    'Race Index': cols[0].get_text(strip=True),
                    'Pla.': cols[1].get_text(strip=True),
                    'Date': cols[2].get_text(strip=True),
                    'RC/Track/Course': cols[3].get_text(strip=True).replace('\n', ' ').strip(),
                    'Dist.': cols[4].get_text(strip=True),
                    'G': cols[5].get_text(strip=True),
                    'Race Class': cols[6].get_text(strip=True),
                    'Dr.': cols[7].get_text(strip=True),
                    'Rtg.': cols[8].get_text(strip=True),
                    'Trainer': cols[9].get_text(strip=True),
                    'Jockey': cols[10].get_text(strip=True),
                    'LBW': cols[11].get_text(strip=True),
                    'Win Odds': cols[12].get_text(strip=True),
                    'Act. Wt.': cols[13].get_text(strip=True),
                    'Running Position': cols[14].get_text(strip=True),
                    'Finish Time': cols[15].get_text(strip=True),
                    'Declar. Horse Wt.': cols[16].get_text(strip=True),
                    'Gear': cols[17].get_text(strip=True),
                }
                race_history.append(race)

    horse_data['race_history'] = race_history
    return horse_data

if __name__ == "__main__":
    horse_id = "HK_2022_H339"
    data = scrape_horse_data(horse_id)
    if data:
        print(json.dumps(data, indent=4))
