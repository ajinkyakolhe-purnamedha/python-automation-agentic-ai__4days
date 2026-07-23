"""Lab 10 · Part A — classify a Product with an open-source model (standalone).

No OpenAI, no agent, no API server. Just a local `transformers` zero-shot
pipeline: given a product's name + description, guess its category from the
catalog's own category list, and compare to the real category.

Run:
    pip install transformers torch        # one-off (~700 MB, CPU is fine)
    python classify_products.py

Fill every `# TODO`.
"""

from transformers import pipeline

# (name, description, true_category) — a few catalog rows to score.
PRODUCTS = [
    ("USB-C Cable", "1m braided charging cable for phones and laptops", "Electronics"),
    ("Yoga Mat", "non-slip exercise mat for home workouts", "Fitness"),
    ("Bluetooth Speaker", "portable wireless speaker with deep bass", "Electronics"),
    ("Resistance Bands", "set of 5 latex bands for strength training", "Fitness"),
]

CATEGORIES = ["Electronics", "Fitness", "Books", "Home"]


def build_classifier():
    """Return a zero-shot-classification pipeline (small CPU model)."""
    # TODO: return pipeline("zero-shot-classification",
    #                       model="typeform/distilbert-base-uncased-mnli")
    raise NotImplementedError


def guess_category(clf, name: str, description: str) -> str:
    """Return the top predicted category for one product."""
    # TODO: call clf(f"{name}. {description}", candidate_labels=CATEGORIES)
    # TODO: return result["labels"][0]   # highest-scoring label
    raise NotImplementedError


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
