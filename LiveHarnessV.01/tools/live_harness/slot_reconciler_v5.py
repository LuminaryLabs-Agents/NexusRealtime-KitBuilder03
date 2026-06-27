from __future__ import annotations

from .slot_reconciler_v4 import reconcile as _reconcile_v4
from .voxel_composition_files_v6 import build_voxel_composition_files_v6


def reconcile(run_dir, run_id):
    import live_harness.slot_reconciler_v4 as v4
    original = v4.build_voxel_composition_files
    v4.build_voxel_composition_files = build_voxel_composition_files_v6
    try:
        return _reconcile_v4(run_dir, run_id)
    finally:
        v4.build_voxel_composition_files = original
