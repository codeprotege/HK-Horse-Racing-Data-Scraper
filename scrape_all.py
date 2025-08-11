import json
import time
from scraper import scrape_horse_data

def scrape_all_horses():
    """
    Reads horse IDs from horse_ids.json, scrapes data for each,
    and saves the combined data to all_horse_data.json.
    """
    try:
        with open("horse_ids.json", "r") as f:
            horse_ids = json.load(f)
    except FileNotFoundError:
        print("Error: horse_ids.json not found.")
        print("Please run id_finder.py first to generate the list of horse IDs.")
        return

    total_ids = len(horse_ids)
    all_horse_data = []

    print(f"Found {total_ids} horse IDs to scrape.")

    for i, horse_id in enumerate(horse_ids):
        print(f"Scraping horse {i + 1} of {total_ids}: {horse_id}")

        # Scrape data for the current horse ID
        data = scrape_horse_data(horse_id)

        if data:
            # Add the horse_id to the data object for reference
            data['horse_id'] = horse_id
            all_horse_data.append(data)
            print(f"  > Successfully scraped data for {horse_id}.")
        else:
            print(f"  > Failed to scrape data for {horse_id}.")

        # Add a delay to be respectful to the server.
        # 1 second is a reasonable starting point.
        time.sleep(1)

    print(f"\nFinished scraping. Scraped data for {len(all_horse_data)} out of {total_ids} horses.")

    # Save the combined data to a file
    with open("all_horse_data.json", "w") as f:
        json.dump(all_horse_data, f, indent=4)

    print("Successfully saved all scraped data to all_horse_data.json")

if __name__ == "__main__":
    scrape_all_horses()
