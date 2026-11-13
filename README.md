# cedwyn-revival-ar

This repository contains the Revival AR webapp.

## Source and mirror mode

The authoritative `split-repos.json` in `unclehowell/cedwyn` currently lists this repository as `mode: mirror` with `old_branch: section/revival-ar`. Until the owner changes that mode, the source of truth for app content is the `section/revival-ar` branch in `unclehowell/cedwyn`.

The scheduled workflow in this repository copies that single branch into this repository's `main`. It reads the mode and source branch from the authoritative Cedwyn manifest; if the manifest, entry or mode cannot be read, the workflow fails closed and does not overwrite `main`.

The mirror deliberately preserves this repository's local `data/central.json` and `tools/sync_central.py` files; those are local derived/catalogue-sync components, not source-branch content.

Do not treat this repository's `main` as the source of truth for app changes while the manifest remains in `mode: mirror`. Do not force-push or delete the retained branch.