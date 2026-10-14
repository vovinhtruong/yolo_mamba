"""
split_dataset.py
Split GRAZ into train/val/test by patient_id (patient-level partitioning,
following the FracDet-v11 approach) to strictly prevent data leakage.

Ratios are variables at the top -- change them anytime without touching
the rest of the logic.

Reads:
    dataset/graz/dataset.csv
    dataset/graz/processed_dataset/images/*.png  (8-bit converted images)
    dataset/graz/processed_dataset/labels/*.txt  (binary fracture labels)

Writes (symlinks, not copies -- saves disk space):
    dataset/graz/split/train/{images,labels}
    dataset/graz/split/val/{images,labels}
    dataset/graz/split/test/{images,labels}
    dataset/graz/data.yaml
"""
import pathlib
import random
import pandas as pd

# ===== Paths =====
ROOT = pathlib.Path("~/VINH_TRUONG/yolo26/dataset/graz").expanduser()
CSV_PATH = ROOT / "dataset.csv"
IMAGES_DIR = ROOT / "processed_dataset" / "images"
LABELS_DIR = ROOT / "processed_dataset" / "labels"
SPLIT_DIR = ROOT / "split"
DATA_YAML_PATH = ROOT / "data.yaml"

# ===== Split ratios (change these anytime) =====
TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

SEED = 42

assert abs(TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0) < 1e-6, \
    "TRAIN_RATIO + VAL_RATIO + TEST_RATIO must equal 1.0"


def assign_splits(patient_ids):
    """Shuffle unique patient ids and assign each one to train/val/test."""
    patients = sorted(patient_ids)
    random.seed(SEED)
    random.shuffle(patients)

    n = len(patients)
    n_train = int(n * TRAIN_RATIO)
    n_val = int(n * VAL_RATIO)
    # remaining goes to test, so rounding never drops a patient

    train_set = set(patients[:n_train])
    val_set = set(patients[n_train:n_train + n_val])
    test_set = set(patients[n_train + n_val:])

    # sanity check: no patient in more than one split
    assert not (train_set & val_set)
    assert not (train_set & test_set)
    assert not (val_set & test_set)

    return train_set, val_set, test_set


def split_of(patient_id, train_set, val_set):
    if patient_id in train_set:
        return "train"
    if patient_id in val_set:
        return "val"
    return "test"


def main():
    df = pd.read_csv(CSV_PATH)
    unique_patients = df["patient_id"].unique()
    print(f"[INFO] Unique patients: {len(unique_patients)}")
    print(f"[INFO] Ratios -> train:{TRAIN_RATIO} val:{VAL_RATIO} test:{TEST_RATIO}")

    train_set, val_set, test_set = assign_splits(unique_patients)
    print(f"[INFO] Patients -> train:{len(train_set)} val:{len(val_set)} test:{len(test_set)}")

    df["split"] = df["patient_id"].apply(lambda pid: split_of(pid, train_set, val_set))

    # create output folders
    for s in ["train", "val", "test"]:
        (SPLIT_DIR / s / "images").mkdir(parents=True, exist_ok=True)
        (SPLIT_DIR / s / "labels").mkdir(parents=True, exist_ok=True)

    counts = {"train": [0, 0], "val": [0, 0], "test": [0, 0]}  # [total, with_fracture]
    missing_img = missing_lbl = 0

    for _, row in df.iterrows():
        stem = row["filestem"]
        split = row["split"]

        img_src = IMAGES_DIR / f"{stem}.png"
        lbl_src = LABELS_DIR / f"{stem}.txt"

        if not img_src.exists():
            missing_img += 1
            continue
        if not lbl_src.exists():
            missing_lbl += 1
            continue

        img_dst = SPLIT_DIR / split / "images" / img_src.name
        lbl_dst = SPLIT_DIR / split / "labels" / lbl_src.name

        if not img_dst.exists():
            img_dst.symlink_to(img_src.resolve())
        if not lbl_dst.exists():
            lbl_dst.symlink_to(lbl_src.resolve())

        counts[split][0] += 1
        if row["fracture_visible"] == 1:
            counts[split][1] += 1

    print("\n[DONE] Split summary:")
    for s in ["train", "val", "test"]:
        total, frac = counts[s]
        print(f"  {s:5s}: {total} images ({frac} fracture, {total - frac} negative)")

    if missing_img or missing_lbl:
        print(f"\n[WARN] missing images: {missing_img}, missing labels: {missing_lbl}")
        print("       -> run image conversion / label prep scripts first.")

    # write data.yaml for YOLO26
    yaml_content = (
        f"path: {SPLIT_DIR}\n"
        f"train: train/images\n"
        f"val: val/images\n"
        f"test: test/images\n"
        f"nc: 1\n"
        f"names: ['fracture']\n"
    )
    DATA_YAML_PATH.write_text(yaml_content)
    print(f"\n[data.yaml written] {DATA_YAML_PATH}")


if __name__ == "__main__":
    main()