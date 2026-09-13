import json


CHALLENGE_CASES_PATH = "data_pipeline/evaluation/dryer_domain_routing_challenge_cases.json"

UNSUPPORTED_APPLIANCE_TERMS = [
    "refrigerator",
    "freezer",
    "dishwasher",
    "oven",
    "stove",
    "washing machine",
    "washer",
    "microwave",
    "air conditioner",
    "water heater",
    "vacuum",
]


def load_cases():
    with open(CHALLENGE_CASES_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def appliance_word_guard(query):
    lowered = query.lower()
    if any(term in lowered for term in UNSUPPORTED_APPLIANCE_TERMS):
        return "reject"
    return "accept"


def main():
    cases = load_cases()
    correct = 0

    print("=== Held-out domain-routing challenge set ===")
    print("The guard was created before these cases were evaluated.\n")

    for case in cases:
        predicted = appliance_word_guard(case["query"])
        is_correct = predicted == case["expected"]
        correct += is_correct
        status = "OK" if is_correct else "MISS"
        print(f"[{status}] {case['query']}")
        print(f"       expected: {case['expected']}; guard predicted: {predicted}")
        print(f"       why: {case['reason']}")

    print(f"\nAccuracy: {correct}/{len(cases)} ({100 * correct / len(cases):.0f}%)")
    print("A miss does not mean the label is wrong; it identifies a limitation of this specific guard.")


if __name__ == "__main__":
    main()
