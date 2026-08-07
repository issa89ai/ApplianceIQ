import json
import os

WIKIS_DIR = "data_pipeline/raw/wikis"


def main():
    troubleshooting = []
    other = []

    for filename in os.listdir(WIKIS_DIR):
        path = os.path.join(WIKIS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            page = json.load(f)

        if page.get("is_troubleshooting"):
            troubleshooting.append(page["title"])
        else:
            other.append(page["title"])

    print(f"Troubleshooting pages: {len(troubleshooting)}")
    for title in troubleshooting:
        print(f"  - {title}")

    print(f"\nOther (non-troubleshooting) pages: {len(other)}")
    for title in other:
        print(f"  - {title}")


if __name__ == "__main__":
    main()