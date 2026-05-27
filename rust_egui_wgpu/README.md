# OmniBoard — Rust / egui / wgpu node-graph demo

A self-contained reimplementation of OmniBoard Studio's core idea in Rust using
**egui** for the immediate-mode UI and **wgpu** as the rendering backend
(via `eframe`): draggable **blocks** with input/output **ports**, bezier
**wires**, a pannable grid canvas, and a sidebar that generates Raspberry Pi
Python from the graph.

`eframe` is configured with `default-features = false` + `features = ["wgpu"]`,
and `main.rs` requests `eframe::Renderer::Wgpu`, so all drawing is submitted
through wgpu (Vulkan / Metal / DX12 / GL depending on platform).

## Controls

| Action | Result |
|--------|--------|
| Left-drag a block | move it (wires follow) |
| Right-click an output port, release on an input port | create a wire |
| Middle-drag | pan the canvas |
| Sidebar buttons | add blocks, clear, generate code |

## Build & run

Requires a recent **Rust toolchain** (`rustup`, stable). On Linux you also need
the usual windowing dev packages (`libxkbcommon`, `libwayland`/`libx11`, etc.).

```sh
cd examples/rust_egui_wgpu
cargo run --release
```

First build downloads and compiles wgpu, so it takes a while; later builds are
fast.

## Files

- `Cargo.toml` — pins `eframe`/`egui` 0.27 with the wgpu backend.
- `src/main.rs` — the whole app: `Block`, `Wire`, and the `eframe::App`
  implementation that draws the canvas with an `egui::Painter`.
