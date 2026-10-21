"""
Build binary "fracture" labels from the ORIGINAL 9-class YOLOv5 labels.

Reads  original_dataset/labels/*.txt   (never modified)
Writes processed_dataset/labels/*.txt  (overwritten every run)
-> safe to run any number of times: the output is always rebuilt from the originals.

Original class ids (see original_dataset/meta.yaml):
  0 boneanomaly
  1 bonelesion
  2 foreignbody
  3 fracture        <-- the only class we keep
  4 metal
  5 periostealreaction
  6 pronatorsign
  7 softtissue
  8 text

Rule per file:
  - Keep only lines where class_id == FRACTURE_CLASS_ID (3)
  - Rewrite that class_id as NEW_CLASS_ID (0)
  - Drop every other line (metal, text, axis, etc.)
  - If no fracture line remains, the output file is EMPTY
    (an empty label file = "background" image, no object, for YOLO)
"""
import pathlib

ROOT = pathlib.Path("~/VINH_TRUONG/yolo26/dataset/graz").expanduser()
SRC_DIR = ROOT / "original_dataset" / "labels"    # read only
OUT_DIR = ROOT / "processed_dataset" / "labels"   # rebuilt from SRC_DIR

FRACTURE_CLASS_ID = "3"
NEW_CLASS_ID = "0"


def convert_file(src: pathlib.Path, dst: pathlib.Path) -> str:
    """Write the binary version of one original label file. Returns 'fracture' or 'empty'."""
    kept_lines = []
    for line in src.read_text().splitlines():
        parts = line.strip().split()
        if parts and parts[0] == FRACTURE_CLASS_ID:
            parts[0] = NEW_CLASS_ID
            kept_lines.append(" ".join(parts))

    dst.write_text("\n".join(kept_lines) + "\n" if kept_lines else "")
    return "fracture" if kept_lines else "empty"


def main():
    if SRC_DIR.resolve() == OUT_DIR.resolve():
        raise SystemExit("[ERROR] SRC_DIR and OUT_DIR must be different folders")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    src_files = sorted(SRC_DIR.glob("*.txt"))
    print(f"[INFO] Found {len(src_files)} original label files in {SRC_DIR}")

    n_fracture = 0
    n_empty = 0
    for i, src in enumerate(src_files, 1):
        if convert_file(src, OUT_DIR / src.name) == "fracture":
            n_fracture += 1
        else:
            n_empty += 1
        if i % 5000 == 0:
            print(f"  ...processed {i}/{len(src_files)}")

    print("\n[DONE]")
    print(f"  Written to             : {OUT_DIR}")
    print(f"  Total files            : {len(src_files)}")
    print(f"  With fracture (class 0): {n_fracture}")
    print(f"  Empty (negative)       : {n_empty}")


if __name__ == "__main__":
    main()