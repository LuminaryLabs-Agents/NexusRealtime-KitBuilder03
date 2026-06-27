from __future__ import annotations

from . import massive_build_loop as base
from . import slot_reconciler_v4
from . import composition_validation_runner

base.reconcile = slot_reconciler_v4.reconcile
base.validate_sandbox = composition_validation_runner.validate_sandbox

main = base.main
run_massive_build = base.run_massive_build

if __name__ == "__main__":
    main()
