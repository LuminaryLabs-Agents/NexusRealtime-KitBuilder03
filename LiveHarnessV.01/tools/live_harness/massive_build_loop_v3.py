from __future__ import annotations

from . import massive_build_loop as base
from . import slot_reconciler_v3

base.reconcile = slot_reconciler_v3.reconcile

main = base.main
run_massive_build = base.run_massive_build

if __name__ == "__main__":
    main()
