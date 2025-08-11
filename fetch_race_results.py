import requests
from bs4 import BeautifulSoup
import json
import argparse
from datetime import datetime
import re

def clean_text(text):
    """Removes extra whitespace and newlines from a string."""
    return ' '.join(text.split())

def fetch_race_results(date_str):
    """
    Fetches race results for a given date from the Hong Kong Jockey Club website.

    Args:
        date_str (str): The date of the race meeting in YYYY-MM-DD format.

    Returns:
        list: A list of dictionaries, where each dictionary represents a race and its results.
    """
    try:
        dt_object = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = dt_object.strftime('%d/%m/%Y')
        url = f"https://racing.hkjc.com/racing/information/English/racing/LocalResults.aspx?RaceDate={formatted_date}"
    except ValueError:
        print("Error: Invalid date format. Please use YYYY-MM-DD.")
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    races = []

    # Find all race tabs which act as anchors for each race's data
    race_tabs = soup.find_all('div', class_='race_tab')

    if not race_tabs:
        print(f"No race results found for {date_str}.")
        return None

    for race_tab in race_tabs:
        race_data = {}

        # Extract race summary
        summary_table = race_tab.find('table')
        if summary_table:
            title_tr = summary_table.find('tr', class_='bg_blue')
            if title_tr:
                race_data['race_summary'] = clean_text(title_tr.text)

        # Find the performance div, which is the next sibling of the race_tab's parent div
        performance_div = race_tab.find_next_sibling('div', class_='performance')
        if performance_div:
            results_table = performance_div.find('table')
            if results_table:
                headers = [clean_text(th.text) for th in results_table.find('thead').find_all('td')]
                rows = []
                for row in results_table.find('tbody').find_all('tr'):
                    cols = row.find_all('td')
                    row_data = {}
                    for i, header in enumerate(headers):
                        if i < len(cols):
                            row_data[header] = clean_text(cols[i].text)
                    rows.append(row_data)
                race_data['results'] = rows

        # Find the dividend tab
        dividend_tab = performance_div.find_next_sibling('div', class_='dividend_tab')
        if dividend_tab:
            dividend_table = dividend_tab.find('table')
            if dividend_table:
                dividends = {}
                current_pool = None
                for row in dividend_table.find('tbody').find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) == 3:
                        pool, combo, dividend = [c.text.strip() for c in cells]
                        current_pool = pool
                        dividends.setdefault(current_pool, []).append({"combination": combo, "dividend": dividend})
                    elif len(cells) == 2:
                        combo, dividend = [c.text.strip() for c in cells]
                        if current_pool:
                            dividends.setdefault(current_pool, []).append({"combination": combo, "dividend": dividend})
                race_data['dividends'] = dividends

        if race_data:
            races.append(race_data)

    return races

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch horse racing results from the HKJC website.')
    parser.add_argument('date', type=str, help='The date of the race meeting in YYYY-MM-DD format.')

    args = parser.parse_args()

    results = fetch_race_results(args.date)

    if results:
        print(json.dumps(results, indent=4))
