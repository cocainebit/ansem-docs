#!/usr/bin/env python3
"""Generate the "Smart Contract Source" docs section from the live contract
source. Re-run after changing any contract so the docs never drift from code.

For each contract it writes one page per .rs file (full source + a short role
note), creates an overview stub the first time (hand-edit it afterwards, it is
never overwritten), and rebuilds the nested nav group in docs.json.

    python3 gen-source-docs.py
"""

import json
import os
from pathlib import Path

DOCS = Path(__file__).resolve().parent
REPO = DOCS.parent.parent  # ansem-chain/
CONTRACTS_DIR = REPO / "contracts"
OUT = DOCS / "source"

# Display order + one-line purpose. Overviews are hand-written; this blurb only
# seeds the stub the first time.
CONTRACTS = [
    ("launchpad", "Launchpad", "Permissionless token launches on a constant-product bonding curve that graduates to the AMM."),
    ("amm", "AMM", "Constant-product automated market maker: pools, swaps, and liquidity for graduated tokens."),
    ("oracle", "Oracle", "On-chain CHANSE/USD price feed used for USD-denominated displays and limits."),
    ("config", "Config Registry", "The single on-chain pointer that every app resolves mutable addresses from (hot-swap)."),
    ("vesting", "Vesting", "Time-locked token release schedules."),
    ("names", "Name Service", "The .ansem name registry."),
    ("proposals", "Proposals", "On-chain community proposals and multi-option voting."),
]

# Standard CosmWasm file roles (accurate across all of these contracts).
FILE_ROLE = {
    "msg.rs": "The public interface: every `InstantiateMsg`, `ExecuteMsg`, `QueryMsg`, and response type. This is the contract's API surface, what you can call and what comes back.",
    "state.rs": "Persistent storage: the structs and storage keys (`Item`/`Map`) that hold the contract's state between calls.",
    "contract.rs": "The logic: the `instantiate`/`execute`/`query` entry points and every handler behind them. This is where the rules actually run.",
    "error.rs": "The typed errors this contract can return, and the conditions that trigger them.",
    "lib.rs": "Module wiring: declares the contract's modules and re-exports.",
    "tests.rs": "Unit tests exercising the contract's logic.",
}

# Render files in a readable order (interface first, logic, then plumbing).
FILE_ORDER = ["msg.rs", "state.rs", "contract.rs", "error.rs", "lib.rs", "tests.rs"]


def file_pages(slug):
    src = CONTRACTS_DIR / slug / "src"
    present = {p.name: p for p in src.glob("*.rs")}
    ordered = [f for f in FILE_ORDER if f in present] + sorted(
        f for f in present if f not in FILE_ORDER
    )
    return [(f, present[f]) for f in ordered]


def yq(s):
    """Escape a value for a single-quoted YAML scalar (double the quotes)."""
    return s.replace("'", "''")


def write_file_page(slug, fname, path):
    base = fname[:-3]  # strip .rs
    role = FILE_ROLE.get(fname, "Contract source file.")
    code = path.read_text()
    loc = code.count("\n") + 1
    out_dir = OUT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    page = (
        "---\n"
        f"title: '{yq(fname)}'\n"
        f"description: '{yq(role.split('.')[0])}.'\n"
        "---\n\n"
        f"{role}\n\n"
        f"<Info>Live source from `contracts/{slug}/src/{fname}` ({loc} lines). "
        "Generated from the deployed contract code.</Info>\n\n"
        "```rust wrap\n"
        f"{code.rstrip()}\n"
        "```\n"
    )
    (out_dir / f"{base}.mdx").write_text(page)
    return base


def write_overview_stub(slug, name, blurb):
    out_dir = OUT / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / "overview.mdx"
    if p.exists():
        return  # hand-edited, never clobber
    p.write_text(
        "---\n"
        f"title: '{yq(name)}'\n"
        f"description: '{yq(blurb)}'\n"
        "---\n\n"
        f"{blurb}\n\n"
        "## What it does\n\n_TODO: hand-written explanation._\n\n"
        "## Interface\n\nSee the message types in the source below.\n"
    )


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    nav_children = ["source/overview"]
    for slug, name, blurb in CONTRACTS:
        if not (CONTRACTS_DIR / slug / "src").is_dir():
            print(f"  skip {slug} (no src)")
            continue
        write_overview_stub(slug, name, blurb)
        pages = [f"source/{slug}/overview"]
        for fname, path in file_pages(slug):
            base = write_file_page(slug, fname, path)
            pages.append(f"source/{slug}/{base}")
        nav_children.append({"group": name, "pages": pages})
        print(f"  {name}: {len(pages) - 1} files")

    # top-level overview stub
    top = OUT / "overview.mdx"
    if not top.exists():
        top.write_text(
            "---\ntitle: 'Smart Contract Source'\n"
            "description: 'Browse the full source of every CHANSE contract, with explanations.'\n---\n\n"
            "_TODO: hand-written intro._\n"
        )

    # inject / replace the nav group in docs.json
    docs_json = DOCS / "docs.json"
    d = json.loads(docs_json.read_text())
    groups = d["navigation"]["groups"]
    group = {"group": "Contract Source", "pages": nav_children}
    for i, g in enumerate(groups):
        if g.get("group") == "Contract Source":
            groups[i] = group
            break
    else:
        groups.append(group)
    docs_json.write_text(json.dumps(d, indent=2) + "\n")
    print(f"nav: 'Contract Source' group with {len(nav_children)} entries")


if __name__ == "__main__":
    build()
