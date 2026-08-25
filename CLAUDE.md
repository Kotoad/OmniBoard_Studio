# OmniBoard Studio

Rust + egui/eframe 0.30 visual block editor. Blocks are wired into a graph that will later be
compiled to device code.

## Verifying work

CI (`.github/workflows/test.yaml`) runs exactly these, and **clippy warnings are errors**:

```
cargo build --locked
cargo clippy -- -D warnings
cargo fmt --check
cargo test
```

Note `clippy` runs without `--all-targets`, so it lints the binary only; run
`cargo clippy --all-targets` locally to catch lints in test code too. Do not report work as
finished until all four pass.

## Layout

| Path | What it owns |
| --- | --- |
| `src/graph.rs` | The data model: `Block`, `Wire`, `BlockKind`, and `Graph` with its indices. All graph mutation goes through here. |
| `src/visual_editor.rs` | Canvas rendering, camera, hit-testing, file save/load, and the editor's own tests. |
| `src/compiler/` | Stubs (`ir`, `lower`, `emit`, `validate`) — codegen and validation land here. |
| `src/omni_format.rs` | Frozen v1/v2 structs, used only to migrate old files. |
| `src/blocks_data.rs`, `src/blocks_library.rs` | Per-block metadata (titles, colors, categories) and the palette UI. |
| `i18n/en`, `i18n/cs` | Fluent translation files. |
| `tests/fixtures/` | `.omni` files pinning the v1 and v2 formats. Never regenerate them. |

## Invariants

`Graph` keeps three derived indices — `block_index`, `out_wire`, `in_wire` — that must never
disagree with `blocks` and `wires`:

- Every mutation funnels through `Graph`'s own methods. Do not hand out `&mut` access that lets a
  caller change a block's `id` or a wire's endpoints.
- `normalize()` is the single rebuild point, and it runs on every load path.
- `repair_wires()` drops wires that are dangling, out of range, or on an already-claimed port.
  Loaded files are untrusted input.
- The wire maps are mutual inverses; at most one wire leaves any output port and at most one enters
  any input port. `(from_block, from_port)` is therefore a unique wire identity.
- `debug_assert` helpers check all of this on every mutation. Keep new mutators asserting too.

In the editor:

- `graphs`, `cameras`, and `wire_caches` are parallel vectors. Anything that resizes one resizes all
  three — see `ok_load`.
- Any edit that changes the document sets `self.dirty = true`, including block moves. The window
  title's `*` depends on it.

## File format

`FORMAT_VERSION` is 3 and is still in development, so it may change without a migration — but the
v1 and v2 readers in `omni_format.rs` and their fixtures must keep working.

Derived data (the indices, `next_block_id`) is `#[serde(skip)]` and rebuilt by `normalize()`. Caches
do not belong in the file: a persisted index is a second source of truth that has to be validated on
load, which costs exactly as much as rebuilding it. `Graph`'s `PartialEq` is hand-written for the
same reason — it compares `name`, `blocks`, and `wires` only.

## Conventions

General working rules and code conventions live in the global `~/.claude/CLAUDE.md`. On top of
those, here:

- User-facing strings go through `LOADER.get(...)` or `fl!(LOADER, "key")`, and every new key is
  added to **both** `i18n/en` and `i18n/cs`.
- Test oracles scan `blocks` / `wires` directly.
- proptest strategies draw ids `0..8` and ports `0..4`, and probe over a wider space so absent ids
  are covered too.

## Tracker

Work is tracked in Linear as `OMN-nn`; reference the issue id in commits and PRs.
