# go-webassembler

A pure-Go assembler API for WebAssembly.

### Goals

- Reasonably fast and simple binary wasm encoding.
- Convenient API for use as part of a compiler written in Go.
- Data-driven instruction set ([details](./internal/instructions/README.md)).
- Append-only stream-per-section design.

### Non-Goals

- Binary wasm decoding or analysis.
- WAT or other text formats.
- Symbolic assembly or other conveniences.
- Machine code generation, etc.
- Component Model, ABIs, etc.
- WebAssembly runtime.
- Other things you'd find in something like WABT.

## Status

Incomplete and unstable. You should probably not use this :)

## Usage

- Use `NewModule()` to get a Module object.
- Call methods directly on Module or the Section objects to append data.
- In particular, create functions with `NewCode()` and `mod.AddFunc`.
- See [instructions.go](./instructions.go) for code assembly methods.
- Assemble a final result by calling `.Bytes()`.
