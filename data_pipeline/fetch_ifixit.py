import json
import requests

BASE_URL = "https://www.ifixit.com/api/2.0"


def search_dryer():
    response = requests.get(f"{BASE_URL}/search/dryer")
    response.raise_for_status()
    return response.json()


def main():
    data = search_dryer()
    with open("data_pipeline/raw/search_dryer.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data['results'])} results to data_pipeline/raw/search_dryer.json")


if __name__ == "__main__":
    main()