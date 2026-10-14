#!/bin/bash
export YOLO_CONFIG_DIR=~/VINH_TRUONG/yolo26/.ultralytics_config

MODEL=~/VINH_TRUONG/yolo26/base_models/yolo26n.pt
EPOCHS=50
BATCH=4

# IMGSZ_LIST=(576 640 1024 1152 1344)  # first time
# IMGSZ_LIST=(1440)                    # second time
# IMGSZ_LIST=(768 896 992 1120 1280)   # P10/P30/P50/P70/P90 of train max_dim, rounded to x32
IMGSZ_LIST=(640 896 1024 1120)         # seed repeat: default + 3 best candidates
SEED_LIST=(1 2)                        # seed 0 = existing runs in runs/multi_size_first_test (Ultralytics default)

for IMGSZ in "${IMGSZ_LIST[@]}"; do
  for SEED in "${SEED_LIST[@]}"; do
    NAME="imgsz${IMGSZ}_seed${SEED}"
    ~/miniconda3/envs/yolo26/bin/yolo detect train \
      model="$MODEL" data=~/VINH_TRUONG/yolo26/dataset/graz/data.yaml \
      epochs="$EPOCHS" imgsz="$IMGSZ" batch="$BATCH" seed="$SEED" device=0 \
      project=~/VINH_TRUONG/yolo26/runs/seed_repeat name="$NAME"
  done
done