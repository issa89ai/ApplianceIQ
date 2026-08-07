import json
import os
import time
import requests

BASE_URL = "https://www.ifixit.com/api/2.0"
RAW_DIR = "data_pipeline/raw"
WIKIS_DIR = os.path.join(RAW_DIR, "wikis")


def load_search_results():
    with open(os.path.join(RAW_DIR, "search_dryer.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_wiki(wikiid):
    response = requests.get(f"{BASE_URL}/wikis/{wikiid}")
    response.raise_for_status()
    return response.json()


def main():
    os.makedirs(WIKIS_DIR, exist_ok=True)
    data = load_search_results()
    wiki_results = [r for r in data["results"] if r["dataType"] == "wiki"]
    print(f"Found {len(wiki_results)} wiki-type results to fetch")

    for i, result in enumerate(wiki_results, start=1):
        wikiid = result["wikiid"]
        out_path = os.path.join(WIKIS_DIR, f"{wikiid}.json")

        if os.path.exists(out_path):
            print(f"[{i}/{len(wiki_results)}] {wikiid} already saved, skipping")
            continue

        print(f"[{i}/{len(wiki_results)}] Fetching {wikiid} - {result['title']}")
        page = fetch_wiki(wikiid)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(page, f, indent=2)

        time.sleep(0.5)


if __name__ == "__main__":
    main()