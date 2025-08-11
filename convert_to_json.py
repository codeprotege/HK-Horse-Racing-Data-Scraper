import json

def convert_to_json():
    """
    Converts the scraped horse data from CSV-like format to JSON.
    """
    data = {}
    try:
        with open('horse_data.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        horse_id, horse_name = parts
                        data[horse_id.strip()] = horse_name.strip()

        with open('horse_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    except FileNotFoundError:
        print("Error: horse_data.txt not found.")

if __name__ == "__main__":
    convert_to_json()
