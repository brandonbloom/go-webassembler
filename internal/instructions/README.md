# WebAssembly Instructions

This directory contains information about WebAssembly instructions.

## Files

- `index.csv`: A CSV file listing all WebAssembly instructions with their opcodes, immediates, and stack effects
- `gen_csv.py`: A Python script that generates the CSV file from instruction data

## CSV Format

The `index.csv` file contains the following columns:

1. `instruction`: The base name of the instruction (e.g., `i32.add`)
2. `immediates`: Any immediate parameters for the instruction (e.g., `memarg` for memory instructions)
3. `opcode`: The hexadecimal opcode(s) for the instruction, without the "0x" prefix
4. `input`: The input stack types for the instruction
5. `output`: The output stack types for the instruction

## Usage

To regenerate the CSV file, run:

```
python3 gen_csv.py
```

This will process the instruction data and output a new `index.csv` file.

## Credits

The instruction data is adapted from the [WebAssembly specification](https://github.com/WebAssembly/spec/blob/05949f507908aac3ad2a21661b5c39fa013da950/document/core/appendix/index-instructions.py).