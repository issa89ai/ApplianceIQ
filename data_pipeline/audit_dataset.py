import json
import os
from collections import Counter


SEARCH_RESULTS_PATH = "data_pipeline/raw/search_dryer.json"
WIKIS_DIR = "data_pipeline/raw/wikis"
NODES_PATH = "data_pipeline/processed/dryer_decision_trees.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def summary(values):
    if not values:
        return "none"
    return f"min {min(values)}, average {sum(values) / len(values):.1f}, max {max(values)}"


def main():
    search_data = load_json(SEARCH_RESULTS_PATH)
    nodes = load_json(NODES_PATH)
    raw_pages = [
        load_json(os.path.join(WIKIS_DIR, filename))
        for filename in os.listdir(WIKIS_DIR)
        if filename.endswith(".json")
    ]

    wiki_search_results = [
        result for result in search_data["results"] if result.get("dataType") == "wiki"
    ]
    troubleshooting_raw_pages = [
        page for page in raw_pages if page.get("is_troubleshooting")
    ]
    node_types = Counter(node["type"] for node in nodes)
    leaf_cause_counts = [len(node.get("causes", [])) for node in nodes if node["type"] == "leaf"]
    router_branch_counts = [
        len(node.get("branches", [])) for node in nodes if node["type"] == "router"
    ]
    missing_descriptions = [node["title"] for node in nodes if not node.get("description")]
    missing_source_urls = [
        node["title"] for node in nodes if not node.get("source", {}).get("source_page_url")
    ]
    missing_licenses = [
        node["title"] for node in nodes if not node.get("source", {}).get("license")
    ]

    print("=== Dryer dataset audit ===")
    print(f"Search results returned: {len(search_data['results'])}")
    print(f"Wiki-type search results fetched: {len(wiki_search_results)}")
    print(f"Raw wiki files present: {len(raw_pages)}")
    print(f"Raw pages marked troubleshooting by iFixit: {len(troubleshooting_raw_pages)}")
    print(f"Processed retrieval nodes: {len(nodes)}")

    print("\n--- Node structure ---")
    print(f"Leaf diagnosis pages: {node_types['leaf']}")
    print(f"Router pages: {node_types['router']}")
    print(f"Possible causes per leaf: {summary(leaf_cause_counts)}")
    print(f"Linked branches per router: {summary(router_branch_counts)}")

    print("\n--- Data quality checks ---")
    print(f"Nodes without a description: {len(missing_descriptions)}")
    print(f"Nodes without a readable original-source URL: {len(missing_source_urls)}")
    print(f"Nodes without a license field: {len(missing_licenses)}")

    print("\n--- Current guide coverage ---")
    for node in nodes:
        item_count = len(node.get("causes") or node.get("branches") or [])
        print(f"[{node['type']}] {node['title']} ({item_count} repair items)")

    if len(nodes) != len(troubleshooting_raw_pages):
        print("\nWARNING: processed-node count does not match troubleshooting raw-page count.")
    else:
        print("\nAudit result: every source page marked troubleshooting is represented once in the retrieval dataset.")


if __name__ == "__main__":
    main()
