#!/bin/bash
export YOLO_CONFIG_DIR=~/VINH_TRUONG/yolo26/.ultralytics_config
# Edit the variables below when you want to change what gets evaluated, then just run this script.

EXPERIMENT=baseline
RUN_NAME=yolo26n_640
WEIGHTS=best.pt
SPLIT=test

~/miniconda3/envs/yolo26/bin/yolo detect val \
  model=~/VINH_TRUONG/yolo26/runs/"$EXPERIMENT"/"$RUN_NAME"/weights/"$WEIGHTS" \
  data=~/VINH_TRUONG/yolo26/dataset/graz/data.yaml \
  split="$SPLIT" \
  project=~/VINH_TRUONG/yolo26/runs/eval name="${RUN_NAME}_${SPLIT}"