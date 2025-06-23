# scraper.py

import requests
from bs4 import BeautifulSoup, NavigableString
import re

def scrape_recipe(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")

    result = {}

    # --- Title ---
    title1_tag = soup.find("h1", class_=re.compile("h2"))
    title2_tag = soup.find("h2", class_=re.compile("h5"))
    result["title1"] = title1_tag.get_text(strip=True) if title1_tag else "Untitled"
    result["title2"] = title2_tag.get_text(strip=True) if title2_tag else ""

    # --- Recipe Type ---
    tag_container = soup.find("p", class_="tag")
    result["recipe_type"] = tag_container.get_text(strip=True) if tag_container else ""

    # --- Main Image ---
    img_tag = soup.find("img", attrs={"data-srcset": True})
    best_img_url = ""
    if img_tag:
        srcset = img_tag["data-srcset"]
        urls = re.findall(r"https://[^ ]+\.jpg", srcset)
        if urls:
            raw = urls[-1]
            match = re.search(r"(https://[^/]*homechef\.com/)(?:cdn-cgi/image/[^/]+)?(/uploads/.*)", raw)
            if match:
                best_img_url = match.group(1).rstrip('/') + match.group(2)
    result["main_image_url"] = best_img_url

    # --- Prep & Cook Time ---
    time_div = soup.find("div", class_="meal__overviewItem")
    result["prep_cook_time"] = ""
    if time_div:
        spans = time_div.find_all("span")
        if len(spans) >= 2:
            result["prep_cook_time"] = spans[1].get_text(strip=True)

    # --- Cook Within / Difficulty / Spice ---
    def extract_meta(label_text):
        for block in soup.find_all("div", class_="meal__overviewItem"):
            label = block.find("span")
            if label and label_text in label.get_text():
                spans = block.find_all("span")
                for span in spans:
                    text = span.get_text(strip=True)
                    if text and not text.startswith(label_text):
                        return text
        return ""

    result["cook_within"] = extract_meta("Cook Within")
    result["difficulty_level"] = extract_meta("Difficulty Level")
    result["spice_level"] = extract_meta("Spice Level")

    # --- You Will Need ---
    result["you_will_need"] = []
    heading = soup.find("h1", string=re.compile("You Will Need", re.IGNORECASE))
    if heading:
        section = heading.find_parent("section")
        if section:
            for ul in section.find_all("ul", class_="meal__utensils"):
                for li in ul.find_all("li"):
                    full_line = li.get_text(separator=" ", strip=True)
                    cleaned = re.sub(r"\s+", " ", full_line).strip()
                    if cleaned:
                        result["you_will_need"].append(cleaned)

    # --- Ingredients ---
    result["ingredients"] = []
    for li in soup.find_all("li", itemprop="recipeIngredient"):
        icon = li.find("div", class_="icon")
        if icon:
            icon.decompose()
        full_text = " ".join(li.stripped_strings)
        cleaned = re.sub(r"\s+", " ", full_text).strip()
        if cleaned:
            result["ingredients"].append(cleaned)

    # --- Before You Cook ---
    result["before_you_cook"] = []
    heading = soup.find("h4", string=re.compile("Before You Cook", re.IGNORECASE))
    if heading:
        section = heading.find_parent("section")
        if section:
            for label in section.find_all("label", class_="text"):
                p = label.find("p")
                if p:
                    fragments = []
                    for elem in p.contents:
                        if isinstance(elem, NavigableString):
                            fragments.append(str(elem).strip())
                        elif elem.name == "strong":
                            fragments.append(f"<b>{elem.get_text(strip=True)}</b>")
                        else:
                            fragments.append(elem.get_text(strip=True))
                    text = " ".join(fragments)
                    cleaned = re.sub(r"\s+", " ", text).strip()
                    result["before_you_cook"].append(cleaned)

    # --- Steps ---
    result["steps"] = []
    for i, li in enumerate(soup.find_all("li", itemprop="itemListElement"), 1):
        # Image
        img = li.find("img", attrs={"data-srcset": True})
        step_img_url = ""
        if img:
            srcset = img.get("data-srcset", "")
            urls = re.findall(r"https://[^ ]+\.jpg", srcset)
            if urls:
                raw = urls[-1]
                match = re.search(r"(https://[^/]*homechef\.com/)(?:cdn-cgi/image/[^/]+)?(/uploads/.*)", raw)
                if match:
                    step_img_url = match.group(1) + "cdn-cgi/image/" + match.group(2)

        # Title
        h4 = li.find("h4", itemprop="name")
        step_title = h4.get_text(strip=True) if h4 else f"Step {i}"

        # Body
        span = li.find("span", itemprop="description")
        step_body = ""
        last_bold = None
        if span:
            fragments = []
            for node in span.descendants:
                if isinstance(node, NavigableString):
                    text = str(node).strip()
                    if text and text != last_bold:
                        fragments.append(text)
                elif node.name == "strong":
                    bold_text = node.get_text(strip=True)
                    fragments.append(f"<b>{bold_text}</b>")
                    last_bold = bold_text
            step_body = "".join(fragments)
            step_body = re.sub(r"\s+", " ", step_body).strip()

        result["steps"].append({
            "title": step_title,
            "image_url": step_img_url,
            "body": step_body
        })

    return result
