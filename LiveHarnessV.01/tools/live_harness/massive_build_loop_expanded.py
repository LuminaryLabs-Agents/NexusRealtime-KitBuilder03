from __future__ import annotations

from . import massive_build_loop as base
from . import slot_reconciler_expanded

base.reconcile = slot_reconciler_expanded.reconcile

main = base.main
run_massive_build = base.run_massive_build

if __name__ == "__main__":
    main()
