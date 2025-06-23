# main.py

import sys, os, json
from scraper import scrape_recipe
from render_html import render_recipe_to_html


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    if len(sys.argv) != 2:
        print("Usage: python main.py <homechef_url>")
        sys.exit(1)

    url = sys.argv[1]
    recipe_data = scrape_recipe(url)

    recipe_type_colors = {
        "Meal Kit": "#2f855a",
        "Fast & Fresh": "#3182ce",
        "Oven-Ready": "#d69e2e"
    }

    #print(json.dumps(recipe_data, indent=2))
    
    render_recipe_to_html(
        recipe_data,
        'front.html',
        'output/front.html',
        extra_context={"recipe_type_colors": recipe_type_colors}
    )


    #render_recipe_to_html(recipe_data, 'back.html', 'output/back.html')

if __name__ == "__main__":
    main()
