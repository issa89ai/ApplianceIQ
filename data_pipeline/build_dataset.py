import json
import os

WIKIS_DIR = "data_pipeline/raw/wikis"
OUTPUT_PATH = "data_pipeline/processed/dryer_decision_trees.json"

COMMENT_SOLUTIONS = "[comment]solutions[/comment]"
COMMENT_CONCLUSION = "[comment]conclusion[/comment]"


def extract_text(node):
    node_type = node.get("type")

    if node_type == "text":
        return node.get("text", "")

    children = node.get("content") or []
    parts = [extract_text(child) for child in children]
    parts = [p for p in parts if p]

    if node_type == "listItem":
        return "- " + " ".join(parts)
    if node_type in ("bulletList", "orderedList"):
        return "\n".join(parts)
    if node_type == "paragraph":
        return "".join(parts)
    return "\n".join(parts)


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
            current = {"title": extract_text(node), "steps": ""}
        elif current is not None:
            text = extract_text(node)
            if text:
                current["steps"] += text + "\n\n"

    if current:
        causes.append(current)

    return causes


def load_troubleshooting_pages():
    pages = []
    for filename in os.listdir(WIKIS_DIR):
        path = os.path.join(WIKIS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            page = json.load(f)
        if page.get("is_troubleshooting"):
            pages.append(page)
    return pages


def build_node(page):
    causes = parse_causes(page["contents_json"])
    description = page.get("description") or ""

    if causes:
        return {
            "wikiid": page["wikiid"],
            "title": page["title"],
            "type": "leaf",
            "description": description,
            "causes": causes,
        }

    branches = [
        {"wikiid": w["wikiid"], "title": w["title"]}
        for w in page.get("linked_wikis", [])
    ]
    return {
        "wikiid": page["wikiid"],
        "title": page["title"],
        "type": "router",
        "description": description,
        "branches": branches,
    }


def main():
    os.makedirs("data_pipeline/processed", exist_ok=True)
    pages = load_troubleshooting_pages()
    print(f"Processing {len(pages)} troubleshooting pages\n")

    tree_nodes = []
    for page in pages:
        node = build_node(page)
        tree_nodes.append(node)
        count = len(node.get("causes") or node.get("branches") or [])
        print(f"  [{node['type']:7}] {node['title']} ({count} items)")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tree_nodes, f, indent=2)

    print(f"\nSaved {len(tree_nodes)} nodes to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()