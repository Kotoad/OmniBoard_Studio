# OmniBoard Studio

**Visual programming for microcontrollers and single-board computers.**

OmniBoard Studio is a desktop application that lets you build programs for Raspberry Pi boards using a drag-and-drop, node-based interface. Design your logic visually as a graph of connected blocks, and OmniBoard Studio compiles it into ready-to-run MicroPython and Python code for your device — no manual syntax required.

Website: <https://www.omniboardstudio.cz>

## Features

- **Visual node editor** — build logic by connecting blocks, timers, and hardware interfaces instead of writing code by hand.
- **Integrated compiler** — translate node graphs into clean MicroPython and Python, ready to deploy to connected devices.
- **Hardware-aware** — native setup workflows for supported Raspberry Pi boards.
- **Built-in code view** — inspect the generated code directly alongside your graph.

## Supported hardware

- Raspberry Pi Pico series
- Raspberry Pi 1 – 5

## Supported platforms

- Windows
- Linux

## Installation

Prebuilt installers for Windows and Linux are available on the **[download page](https://www.omniboardstudio.cz)**. This is the recommended way to get the app.

### Building from source (optional)

The source in this repository is provided for transparency and reference. To build it yourself you'll need a recent [Rust toolchain](https://rustup.rs):

```bash
cargo build --release
```

The compiled binary will be in `target/release/`.

## Documentation

Tutorials and answers to common questions are on the website — from first-time hardware setup to building your own node diagrams. See the **Tutorials** and **FAQ** pages at <https://www.omniboardstudio.cz>.

## License

Copyright © 2026 OmniBoard Studio.

OmniBoard Studio is **source-available, not open source.** It is released under the [PolyForm Strict License 1.0.0](LICENCE.txt).

In short, the license lets you:

- **view** the source code, and
- **use** the software for **noncommercial and personal purposes** — study, hobby projects, education, and research.

It does **not** permit you to:

- **redistribute** the software,
- **modify it or create derivative works**, or
- use it for **commercial purposes**.

For commercial use, or any rights beyond those above, get in touch through the [website](https://www.omniboardstudio.cz). The full terms are in [`LICENCE.txt`](LICENCE.txt).

## Contributing

Because OmniBoard Studio is source-available under a strict license, it does not accept external code contributions or forks for redistribution. Bug reports and feature suggestions are welcome through the issue tracker.