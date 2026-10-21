#!/usr/bin/env python3
"""Identify which YOLO26 size (n/s/m/l/x) a checkpoint was trained with,
by counting its parameters. This works even after resume (unlike the
'model' field in args.yaml, which gets overwritten to the checkpoint path)
because the architecture itself never changes across a resume.

Reference param counts (fused, from Ultralytics official docs):
  n=2.4M  s=9.5M  m=20.4M  l=24.8M  x=55.7M
Note: a raw (not yet fused) checkpoint may count slightly higher than these
fused numbers, but the gap between sizes is wide enough that this still
matches unambiguously.
"""
import sys

import torch

REFERENCE = {"n": 2.4e6, "s": 9.5e6, "m": 20.4e6, "l": 24.8e6, "x": 55.7e6}


def identify(ckpt_path: str):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = ckpt["model"]
    n_params = sum(p.numel() for p in model.parameters())
    print(f"{ckpt_path}: {n_params:,} parameters ({n_params/1e6:.2f}M)")
    closest = min(REFERENCE, key=lambda k: abs(REFERENCE[k] - n_params))
    print(f"  -> closest match: yolo26{closest}")


if __name__ == "__main__":
    for path in sys.argv[1:]:
        identify(path)