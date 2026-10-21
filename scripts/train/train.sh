#!/bin/bash
export YOLO_CONFIG_DIR=~/VINH_TRUONG/yolo26/.ultralytics_config
# Edit the variables below when you want to change training settings, then just run this script.

MODEL=~/VINH_TRUONG/yolo26/base_models/yolo26n.pt
IMGSZ_LIST=(640 768 896 992 1120 1280)
SEED=0
BATCH=4
EPOCHS=50
PROJECT=~/VINH_TRUONG/yolo26/runs/train/input_size

for IMGSZ in "${IMGSZ_LIST[@]}"; do
  NAME=imgsz${IMGSZ}_seed${SEED}    # e.g. imgsz640_seed0
  ~/miniconda3/envs/yolo26/bin/yolo detect train \
    model="$MODEL" \
    data=~/VINH_TRUONG/yolo26/dataset/graz/data.yaml \
    epochs="$EPOCHS" \
    imgsz="$IMGSZ" \
    batch="$BATCH" \
    seed="$SEED" \
    device=0 \
    project="$PROJECT" name="$NAME"
done