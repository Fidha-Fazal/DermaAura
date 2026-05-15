import argparse
import ast
import csv
import hashlib
import json
import os
import random
import shutil
import urllib.error
import urllib.request
from pathlib import Path


SCIN_CASES_URL = "https://storage.googleapis.com/dx-scin-public-data/dataset/scin_cases.csv"
SCIN_LABELS_URL = "https://storage.googleapis.com/dx-scin-public-data/dataset/scin_labels.csv"
SCIN_IMAGE_PREFIX = "https://storage.googleapis.com/dx-scin-public-data/"
CLASS_NAMES = ("acne", "dry", "normal", "oily")


def download_file(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, open(destination, "wb") as output_file:
        shutil.copyfileobj(response, output_file)


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def merge_case_and_label_rows(cases_rows, label_rows):
    labels_by_case = {row["case_id"]: row for row in label_rows}
    merged = []
    for row in cases_rows:
        combined = dict(row)
        combined.update(labels_by_case.get(row["case_id"], {}))
        merged.append(combined)
    return merged


def parse_weighted_label(raw_value):
    if not raw_value:
        return {}
    try:
        return ast.literal_eval(raw_value)
    except (ValueError, SyntaxError):
        return {}


def normalize_text(value):
    return (value or "").strip().lower()


def infer_scin_label(row):
    """Weakly map SCIN metadata into app base classes.

    This is intentionally conservative:
    - `acne` can be mapped reasonably.
    - `normal` can be weakly mapped from healthy-looking cases.
    - `dry` can be weakly mapped from rough/flaky + dermatitis/eczema-like signals.
    - `oily` is not reliably represented in SCIN and is not auto-labeled here.
    """
    related_category = normalize_text(row.get("related_category"))
    weighted = {normalize_text(key): value for key, value in parse_weighted_label(row.get("weighted_skin_condition_label")).items()}
    rough_or_flaky = normalize_text(row.get("textures_rough_or_flaky")) in {"true", "yes", "1"}
    itching = normalize_text(row.get("condition_symptoms_itching")) in {"true", "yes", "1"}
    painful = normalize_text(row.get("condition_symptoms_pain")) in {"true", "yes", "1"}

    if related_category == "acne" or any("acne" in label for label in weighted):
        return "acne", 0.95, "scin_acne_mapping"

    if related_category == "looks_healthy":
        return "normal", 0.72, "scin_healthy_mapping"

    if rough_or_flaky:
        if any(token in label for label in weighted for token in ("eczema", "dermatitis", "xerosis", "dry")):
            return "dry", 0.68, "scin_rough_flaky_dermatitis_mapping"
        if related_category == "rash" and (itching or painful):
            return "dry", 0.52, "scin_rough_flaky_rash_mapping"

    return None, 0.0, "unmapped"


def choose_split(case_id):
    digest = int(hashlib.md5(case_id.encode("utf-8")).hexdigest(), 16) % 100
    if digest < 70:
        return "train"
    if digest < 85:
        return "val"
    return "test"


def best_image_path(row):
    for column in ("image_1_path", "image_2_path", "image_3_path"):
        value = row.get(column)
        if value:
            return value
    return None


def download_image(relative_path, destination):
    url = SCIN_IMAGE_PREFIX + relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    download_file(url, destination)


def prepare_scin_dataset(output_root, cache_root, manifest_path, download_images=False, limit=None, seed=42):
    random.seed(seed)
    cache_root.mkdir(parents=True, exist_ok=True)

    cases_csv = cache_root / "scin_cases.csv"
    labels_csv = cache_root / "scin_labels.csv"

    if not cases_csv.exists():
        download_file(SCIN_CASES_URL, cases_csv)
    if not labels_csv.exists():
        download_file(SCIN_LABELS_URL, labels_csv)

    merged_rows = merge_case_and_label_rows(load_csv(cases_csv), load_csv(labels_csv))
    random.shuffle(merged_rows)

    manifest_rows = []
    written_counts = {label: 0 for label in CLASS_NAMES}
    reviewed_count = 0

    for row in merged_rows:
        label, confidence, source = infer_scin_label(row)
        if not label:
            continue

        image_path = best_image_path(row)
        if not image_path:
            continue

        split = choose_split(row["case_id"])
        filename = f"{row['case_id']}_{Path(image_path).name}"
        dataset_path = output_root / split / label / filename
        cache_image_path = cache_root / "images" / filename

        if download_images:
            try:
                if not cache_image_path.exists():
                    download_image(image_path, cache_image_path)
                dataset_path.parent.mkdir(parents=True, exist_ok=True)
                if not dataset_path.exists():
                    shutil.copy2(cache_image_path, dataset_path)
            except urllib.error.URLError as exc:
                print(json.dumps({"download_error": str(exc), "image_path": image_path}))
                continue

        manifest_rows.append({
            "case_id": row["case_id"],
            "source_dataset": "SCIN",
            "target_label": label,
            "confidence": round(confidence, 3),
            "mapping_source": source,
            "split": split,
            "image_path": str(dataset_path if download_images else image_path),
            "review_required": "yes" if confidence < 0.70 else "recommended",
        })
        written_counts[label] += 1
        if confidence < 0.70:
            reviewed_count += 1

        if limit and len(manifest_rows) >= limit:
            break

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(manifest_rows[0].keys()) if manifest_rows else [
            "case_id", "source_dataset", "target_label", "confidence", "mapping_source",
            "split", "image_path", "review_required"
        ])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(json.dumps({
        "manifest_path": str(manifest_path),
        "download_images": download_images,
        "counts": written_counts,
        "review_required_rows": reviewed_count,
        "note": "SCIN is strongest for acne and some dry/normal weak labels; oily usually still needs webcam/custom data.",
    }, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Prepare a weakly-labeled public skin dataset from SCIN.")
    parser.add_argument("--output-root", default="data/skin_types", help="Dataset root for train/val/test folders")
    parser.add_argument("--cache-root", default="data/public_sources/scin_cache", help="Cache location for downloaded SCIN metadata/images")
    parser.add_argument("--manifest-path", default="data/public_sources/scin_manifest.csv", help="Where to write the generated manifest CSV")
    parser.add_argument("--download-images", action="store_true", help="Download mapped images into the dataset folders")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of mapped samples to process")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for row order")
    args = parser.parse_args()

    prepare_scin_dataset(
        output_root=Path(args.output_root),
        cache_root=Path(args.cache_root),
        manifest_path=Path(args.manifest_path),
        download_images=args.download_images,
        limit=args.limit or None,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
