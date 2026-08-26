# bwick-docs → ansem docs rebrand

This repo was cloned from `codeberg.org/danishorca/bwick-docs` and rebranded to
ansem on 2026-08-21 (branch `ansem-rebrand`). Below is what changed, the model
it now reflects, and the open items a human should decide before publishing.

## The token model (the important part)

BWICK used one token as both the brand and the gas asset. ansem splits them:

- **CHANSE** (`uchanse`, 6 decimals) is the native **gas + staking + fee** token
  of ansemchain. It inherits BWICK's "a token that grew its own chain,
  zero-inflation, supply constant across both chains" story — that story is true
  for CHANSE. Max supply 1,000,000,000.
- **ANSEM** (`uansem`, 6 decimals) is a **separate bridged voucher asset**, 1:1
  with the pump.fun SPL `9cRCn9rGT8V2imeM2BaKs13yhMEais3ruM3rPvTGpump`. It is
  tradeable and bridgeable but is **not** gas or staking.

The rebrand was done semantically, not as a blind find/replace: the gas token
maps to CHANSE, the chain/brand maps to ansem/ansemchain, and code identifiers
map to the real contract names (`ansem_*`, `AnsemExecutor`, `UpdateAnsemPrice`,
env prefix `ANSEM_`) rather than to CHANSE.

## What changed

- **Chain/brand:** `bwickchain`→`ansemchain`, `bwickd`→`ansemd`, `bwick-1`→
  `ansem-1`, prefix `bwick1`→`ansem1`, `*.bwick.fun`→`*.ansemchain.fun`, socials to
  `x.com/ansemchainfun` / `github.com/ansem-labs`.
- **Denom:** `ubwick`→`uchanse` throughout; the token display is CHANSE.
- **Bridge section (largest change):** rewritten from single-asset to the real
  **multi-asset** design — `assets[]` params, a vault per mint, CHANSE as the
  priority asset plus ANSEM, per-asset mint/burn caps and admin-approval
  threshold, escrow-based withdrawals, Token-2022, per-denom supply
  conservation, program renamed `ansem-bridge`.
- **Dual-token framing** added to introduction, chain/overview (a second-denom
  section), wallet, telegram, explorer, proposals.
- **Economics corrected to the real launchpad contract:** fixed supply 100,000
  tokens, 79,310 (79.31%) on the curve, 20,690 (20.69%) reserved and locked as
  LP at graduation, 0.5% buy / 3.5% sell, 2.25% max wallet, graduation at a
  target market cap (oracle-driven, not a fixed CHANSE raise). Earlier docs
  carried a wrong fixed "15M / 10M CHANSE raise" and "12.5% reserved" — removed.
- **docs.json / custom.css:** name `ansemchain`, palette shifted from BWICK
  orange to the ansem green (`#1f9e40`).
- **source/overview.mdx:** noted the source browser is auto-generated and is
  missing two shipped contracts (certificate, multiplier).
- Proposal cost corrected from a wrong "100 CHANSE" to the real 1-`uchanse`
  memo transfer.

## Open items to decide before publishing

1. **Logo/favicon** — DONE. `logo/light.png`, `logo/dark.png`, `favicon.png`
   are now the ansem bull-coin art (converted from the supplied webp). No BWICK
   artwork remains; the old `mint.json.legacy-bak` (BWICK config) was deleted.
2. **Domains.** Site `ansemchain.fun`; endpoints `rpc.ansemchain.fun` /
   `rest.ansemchain.fun` / `api.ansemchain.fun` are referenced as live but were
   not confirmed registered. Live testnet today is val1 `195.72.61.234`
   (RPC 26657 / REST 1317). Socials: X/Telegram `@ansemchainfun`.
3. **Telegram handles** — DONE. Bots are `@chansetradebot`, `@chansebridgebot`,
   `@chanseproposalbot` throughout.
7. **"Cosmos" mentions.** All removable prose is gone. What remains is
   load-bearing and kept intentionally: REST paths (`/cosmos/bank/...`),
   protobuf type URLs, the `@cosmjs` libraries, and the `cosmos_sdk_version`
   field the node returns — removing these would make the API docs wrong.
8. **CLI install.** Docs and the package now use `npx @ansemchain/ansem`
   (the package was renamed from `ansem` to the scoped `@ansemchain/ansem`;
   publish needs `--access public` and the `@ansemchain` npm scope to exist).
4. **Example addresses.** All `ansem1…` addresses are illustrative; the prefix
   swap left them with invalid bech32 checksums. Real deployed addresses come
   from the on-chain config registry and change per deploy — don't present any
   specific one as canonical.
5. **`source/` is stale and auto-generated.** It still shows a pre-BWICK `dot_*`
   identifier layer in `source/amm/` and omits certificate + multiplier.
   Regenerate with `gen-source-docs.py` against `~/ansemchain/contracts`.
6. **Wallet extension / Chrome Web Store listing** referenced in wallet/install
   may not be published yet.

## Rebuild the source browser

```
python3 gen-source-docs.py   # run against ~/ansemchain/contracts
```
