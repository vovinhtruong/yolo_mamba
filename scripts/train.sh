#!/bin/bash
export YOLO_CONFIG_DIR=~/VINH_TRUONG/yolo26/.ultralytics_config
# Edit the variables below when you want to change training settings, then just run this script.

MODEL=~/VINH_TRUONG/yolo26/base_models/yolo26n.pt
NAME=yolo26n_640
EPOCHS=50

~/miniconda3/envs/yolo26/bin/yolo detect train \
  model="$MODEL" \
  data=~/VINH_TRUONG/yolo26/dataset/graz/data.yaml \
  epochs="$EPOCHS" \
  imgsz=640 \
  batch=16 \
  device=0 \
  project=~/VINH_TRUONG/yolo26/runs/baseline name="$NAME"