# main.py

import sys
import os
from scraper import scrape_recipe
import json

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    if len(sys.argv) != 2:
        print("Usage: python main.py <homechef_url>")
        sys.exit(1)

    url = sys.argv[1]
    recipe_data = scrape_recipe(url)

    print(json.dumps(recipe_data, indent=2))

if __name__ == "__main__":
    main()
