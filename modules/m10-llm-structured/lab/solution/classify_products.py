"""Lab 10 · Part A — classify a Product with an open-source model (SOLUTION)."""

from transformers import pipeline

PRODUCTS = [
    ("USB-C Cable", "1m braided charging cable for phones and laptops", "Electronics"),
    ("Yoga Mat", "non-slip exercise mat for home workouts", "Fitness"),
    ("Bluetooth Speaker", "portable wireless speaker with deep bass", "Electronics"),
    ("Resistance Bands", "set of 5 latex bands for strength training", "Fitness"),
]

CATEGORIES = ["Electronics", "Fitness", "Books", "Home"]


def build_classifier():
    return pipeline("zero-shot-classification",
                    model="typeform/distilbert-base-uncased-mnli")


def guess_category(clf, name: str, description: str) -> str:
    result = clf(f"{name}. {description}", candidate_labels=CATEGORIES)
    return result["labels"][0]


def main() -> None:
    clf = build_classifier()
    correct = 0
    for name, desc, true_cat in PRODUCTS:
        pred = guess_category(clf, name, desc)
        hit = "OK " if pred == true_cat else "MISS"
        correct += pred == true_cat
        print(f"[{hit}] {name:18s} pred={pred:12s} true={true_cat}")
    print(f"\n{correct}/{len(PRODUCTS)} correct")


if __name__ == "__main__":
    main()
