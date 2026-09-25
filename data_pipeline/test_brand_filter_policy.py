from backend.main import search


CASES = [
    {
        "name": "generic heating query",
        "query": "my dryer tumbles but does not heat",
        "expected_brand": None,
    },
    {
        "name": "Samsung heating query",
        "query": "my Samsung dryer runs but leaves the clothes cold",
        "expected_brand": "Samsung",
    },
    {
        "name": "LG D80 code query",
        "query": "the dryer display shows D80",
        "expected_brand": "LG",
    },
]


def brand_of(result):
    return result.get("brand")


def main():
    failures = []

    for case in CASES:
        failure_count_before = len(failures)
        results = search(case["query"], top_k=3)["results"]
        expected_brand = case["expected_brand"]

        if not results:
            failures.append(f'{case["name"]}: no results returned')
            print(f'{case["name"]}: FAIL (no results)')
            continue

        returned_brands = [
            brand_of(result) or "generic"
            for result in results
        ]

        if expected_brand is None:
            wrong_results = [
                result["title"]
                for result in results
                if brand_of(result)
            ]

            if wrong_results:
                failures.append(
                    f'{case["name"]}: brand-specific guides returned: '
                    f'{wrong_results}'
                )

        else:
            wrong_results = [
                result["title"]
                for result in results
                if brand_of(result) not in (None, "", expected_brand)
            ]

            if wrong_results:
                failures.append(
                    f'{case["name"]}: wrong-brand guides returned: '
                    f'{wrong_results}'
                )

            if brand_of(results[0]) != expected_brand:
                failures.append(
                    f'{case["name"]}: expected {expected_brand} first, '
                    f'got {results[0]["title"]}'
                )

        status = "PASS" if len(failures) == failure_count_before else "FAIL"
        print(f'{case["name"]}: {status}')
        print(f'  brands: {returned_brands}')

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nAll brand-filter policy tests passed.")


if __name__ == "__main__":
    main()
