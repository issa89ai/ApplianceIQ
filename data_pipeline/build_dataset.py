import json
import os
import re

WIKIS_DIR = "data_pipeline/raw/wikis"
SEARCH_RESULTS_PATH = "data_pipeline/raw/search_dryer.json"
OUTPUT_PATH = "data_pipeline/processed/dryer_decision_trees.json"

COMMENT_SOLUTIONS = "[comment]solutions[/comment]"
COMMENT_CONCLUSION = "[comment]conclusion[/comment]"

IMAGE_MARKUP_RE = re.compile(r"\[image\|[^\]]*\]")
TABLE_BLOCK_RE = re.compile(r"\{table.*?\}", re.DOTALL)
LINK_MARKUP_RE = re.compile(
    r"\[(?:guide|product)\|[^|\]]+\|([^|\]]+)(?:\|[^\]]*)?\]"
)

NAVIGATION_ONLY_LINES = [
    re.compile(r"^here(?:'s| is) (?:a )?(?:helpful )?(?:video|link)\.?$", re.IGNORECASE),
    re.compile(
        r"^for more (?:info(?:rmation)?|tips).{0,120}"
        r"(?:this|our) (?:page|article)\.?$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(?:see|refer to|go to).{0,120}"
        r"(?:above|below|this|our).{0,80}"
        r"(?:page|article|guide|section|step)\.?$",
        re.IGNORECASE,
    ),
]

INLINE_NAVIGATION_PATTERNS = [
    re.compile(
        r"\s*(?:here(?:'s| is) (?:a )?(?:(?:good|helpful) )?"
        r"(?:video|link)[^.\n]*\.?)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\s*for more (?:info(?:rmation)?|tips|details)[^.\n]*"
        r"(?:check out|see|refer to)[^.\n]*"
        r"(?:page|article|guide|video)\.?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\s*more details on [^.\n]*(?:page|article|guide)\.?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\s*if you came here from [^.\n]*?use this link to go back\.?",
        re.IGNORECASE,
    ),
    re.compile(
        r"\s*\(\s*(?:see )?below\s*\)",
        re.IGNORECASE,
    ),
]

IFIXIT_LICENSE = "CC BY-NC-SA 3.0"
IFIXIT_LICENSE_URL = "https://creativecommons.org/licenses/by-nc-sa/3.0/"

KNOWN_BRANDS = [
    "Whirlpool",
    "Samsung",
    "Kenmore",
    "GE",
    "Maytag",
    "LG",
]


def detect_brand(title):
    for brand in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", title, re.IGNORECASE):
            return brand

    return None

def load_source_page_urls():
    with open(SEARCH_RESULTS_PATH, "r", encoding="utf-8") as file:
        search_data = json.load(file)

    return {
        item["wikiid"]: item["url"]
        for item in search_data["results"]
        if item.get("wikiid") and item.get("url")
    }
SOURCE_PAGE_URLS = load_source_page_urls()


def build_source_metadata(page):
    wikiid = page["wikiid"]

    return {
        "provider": "iFixit",
        "source_page_id": wikiid,
        "source_page_url": SOURCE_PAGE_URLS.get(wikiid),
        "source_api_url": f"https://www.ifixit.com/api/2.0/wikis/{wikiid}",
        "license": IFIXIT_LICENSE,
        "license_url": IFIXIT_LICENSE_URL,
        "source_modified_unix": page.get("modified_date"),
        "adapted_for_applianceiq": True,
    }

def extract_text(node):
    node_type = node.get("type")

    if node_type == "text":
        return node.get("text", "")

    children = node.get("content") or []
    parts = [extract_text(child) for child in children]
    parts = [part for part in parts if part]

    if node_type == "listItem":
        return "- " + " ".join(parts)
    if node_type in ("bulletList", "orderedList"):
        return "\n".join(parts)
    if node_type == "paragraph":
        return "".join(parts)
    return "\n".join(parts)


def clean_repair_text(text):
    text = TABLE_BLOCK_RE.sub("", text)
    text = IMAGE_MARKUP_RE.sub("", text)
    text = LINK_MARKUP_RE.sub(r"\1", text)

    for pattern in INLINE_NAVIGATION_PATTERNS:
        text = pattern.sub("", text)

    cleaned_lines = []

    for raw_line in text.splitlines():
        line = " ".join(raw_line.split())

        if not line or line == "-":
            continue

        if any(pattern.match(line) for pattern in NAVIGATION_ONLY_LINES):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def is_comment(node, marker):
    return extract_text(node).strip() == marker


def parse_causes(contents_json):
    nodes = contents_json.get("content", [])
    capturing = False
    causes = []
    current = None

    for node in nodes:
        if is_comment(node, COMMENT_SOLUTIONS):
            capturing = True
            continue

        if is_comment(node, COMMENT_CONCLUSION):
            capturing = False
            continue

        if not capturing:
            continue

        if node.get("type") == "heading":
            if current:
                causes.append(current)

            current = {
                "title": clean_repair_text(extract_text(node)),
                "steps": "",
            }
        elif current is not None:
            text = clean_repair_text(extract_text(node))

            if text:
                current["steps"] += text + "\n\n"

    if current:
        current["steps"] = current["steps"].strip()
        causes.append(current)

    return causes


def load_troubleshooting_pages():
    pages = []

    for filename in os.listdir(WIKIS_DIR):
        path = os.path.join(WIKIS_DIR, filename)

        with open(path, "r", encoding="utf-8") as file:
            page = json.load(file)

        if page.get("is_troubleshooting"):
            pages.append(page)

    return pages


def build_node(page):
    causes = parse_causes(page["contents_json"])
    title = clean_repair_text(page["title"])
    description = clean_repair_text(page.get("description") or "")
    source = build_source_metadata(page)
    brand = detect_brand(title)

    if causes:
        return {
            "wikiid": page["wikiid"],
            "title": title,
            "brand": brand,
            "type": "leaf",
            "description": description,
            "source": source,
            "causes": causes,
        }

    branches = [
        {
            "wikiid": wiki["wikiid"],
            "title": clean_repair_text(wiki["title"]),
        }
        for wiki in page.get("linked_wikis", [])
    ]


    return {
        "wikiid": page["wikiid"],
        "title": title,
        "brand": brand,
        "type": "router",
        "description": description,
        "branches": branches,
        "source": source,
    }

def main():
    os.makedirs("data_pipeline/processed", exist_ok=True)
    pages = load_troubleshooting_pages()

    print(f"Processing {len(pages)} troubleshooting pages\n")

    tree_nodes = []

    for page in pages:
        node = build_node(page)
        tree_nodes.append(node)

        item_count = len(node.get("causes") or node.get("branches") or [])
        print(f"  [{node['type']:7}] {node['title']} ({item_count} items)")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(tree_nodes, file, indent=2)

    print(f"\nSaved {len(tree_nodes)} cleaned nodes to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()