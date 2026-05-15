import argparse
import random
import shutil
import zipfile
from pathlib import Path


LABEL_MAP = {
    "oily": "oily",
    "dry": "dry",
    "normal": "normal",
    "acne": "acne",
    "oil": "oily",
    "oily skin": "oily",
    "dry skin": "dry",
    "normal skin": "normal",
}


def normalize_label(name):
    normalized = name.strip().lower().replace("_", " ").replace("-", " ")
    return LABEL_MAP.get(normalized)


def extract_if_needed(source_path, working_dir):
    source_path = Path(source_path)
    if source_path.is_dir():
        return source_path

    extract_dir = Path(working_dir) / source_path.stem
    if extract_dir.exists():
        return extract_dir

    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source_path, "r") as archive:
        archive.extractall(extract_dir)
    return extract_dir


def find_label_dirs(root):
    discovered = {}
    for path in root.rglob("*"):
        if path.is_dir():
            label = normalize_label(path.name)
            if label and label not in discovered:
                discovered[label] = path
    return discovered


def choose_split(rng):
    value = rng.random()
    if value < 0.70:
        return "train"
    if value < 0.85:
        return "val"
    return "test"


def import_dataset(source_path, dataset_root, working_dir, limit_per_label=None, seed=42):
    rng = random.Random(seed)
    extracted_root = extract_if_needed(source_path, working_dir)
    label_dirs = find_label_dirs(extracted_root)

    imported_counts = {label: 0 for label in sorted(set(LABEL_MAP.values()))}
    for label, label_dir in label_dirs.items():
        images = [path for path in label_dir.rglob("*") if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        rng.shuffle(images)
        if limit_per_label:
            images = images[:limit_per_label]

        for index, image_path in enumerate(images, start=1):
            split = choose_split(rng)
            destination_dir = Path(dataset_root) / split / label
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / f"{image_path.stem}_{index:04d}{image_path.suffix.lower()}"
            shutil.copy2(image_path, destination)
            imported_counts[label] += 1

    print(imported_counts)
    print(f"Imported dataset from {extracted_root} into {dataset_root}")


def main():
    parser = argparse.ArgumentParser(description="Import a local oily/dry/normal skin type dataset into DermaAura format.")
    parser.add_argument("--source", required=True, help="Path to a dataset folder or zip file")
    parser.add_argument("--dataset-root", default="data/skin_types", help="Destination dataset root")
    parser.add_argument("--working-dir", default="data/public_sources/imports", help="Extraction/cache directory for archives")
    parser.add_argument("--limit-per-label", type=int, default=0, help="Optional cap per label")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for split assignment")
    args = parser.parse_args()

    import_dataset(
        source_path=args.source,
        dataset_root=args.dataset_root,
        working_dir=args.working_dir,
        limit_per_label=args.limit_per_label or None,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
