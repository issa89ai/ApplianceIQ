import json

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


def main():
    with open("data_pipeline/raw/wikis/479830.json", "r", encoding="utf-8") as f:
        page = json.load(f)

    causes = parse_causes(page["contents_json"])

    print(f"Title: {page['title']}")
    print(f"Found {len(causes)} causes:\n")
    for cause in causes:
        print(f"=== {cause['title']} ===")
        print(cause["steps"][:300])
        print("...\n")


if __name__ == "__main__":
    main()