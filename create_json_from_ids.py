import json

try:
    with open('horse_ids.txt', 'r') as f:
        horse_ids = [line.strip() for line in f if line.strip()]

    if horse_ids:
        output_data = [{"id": horse_id} for horse_id in horse_ids]
        with open('horses.json', 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f"Successfully created horses.json with {len(horse_ids)} horse IDs.")
    else:
        print("horse_ids.txt is empty.")

except FileNotFoundError:
    print("Error: horse_ids.txt not found.")
