// Package webassembler provides tools for generating WebAssembly binary code.
package webassembler

import (
	"encoding/binary"
	"math"
)

//go:generate sh -c "go run internal/cmd/codegen/main.go <internal/instructions/index.csv >instructions.go"

// Writer is an interface for low-level WebAssembly binary code generation.
type Writer interface {
	// WriteByte appends a single byte to the code.
	WriteByte(b byte)
	// WriteI32 writes a signed 32-bit integer in LEB128 format.
	WriteI32(v int32)
	// WriteI64 writes a signed 64-bit integer in LEB128 format.
	WriteI64(v int64)
	// WriteF32 writes a 32-bit floating point number.
	WriteF32(v float32)
	// WriteF64 writes a 64-bit floating point number.
	WriteF64(v float64)
	// WriteI128 writes a 128-bit value (for v128 constants).
	WriteI128(v [16]byte)
	// WriteIndex writes an unsigned integer index value using LEB128 encoding.
	WriteIndex(v uint32)
	// WriteLEB128Unsigned writes an unsigned integer in LEB128 format.
	WriteLEB128Unsigned(v uint64)
	// WriteLEB128Signed writes a signed integer in LEB128 format.
	WriteLEB128Signed(v int64)
	// MemArg writes memory arguments (alignment and offset).
	MemArg(align, offset uint32)
}

// ByteWriter is an implementation of Writer that stores code in a byte slice.
type ByteWriter struct {
	Code []byte
}

// NewByteWriter creates a new empty byte writer.
func NewByteWriter() *ByteWriter {
	return &ByteWriter{
		Code: make([]byte, 0, 64), // Pre-allocate some space
	}
}

// Reset clears the code buffer.
func (w *ByteWriter) Reset() {
	w.Code = w.Code[:0]
}

// Bytes returns the assembled code.
func (w *ByteWriter) Bytes() []byte {
	return w.Code
}

// WriteByte appends a single byte to the code.
func (w *ByteWriter) WriteByte(b byte) {
	w.Code = append(w.Code, b)
}

// WriteI32 writes a signed 32-bit integer in LEB128 format.
func (w *ByteWriter) WriteI32(v int32) {
	w.WriteLEB128Signed(int64(v))
}

// WriteI64 writes a signed 64-bit integer in LEB128 format.
func (w *ByteWriter) WriteI64(v int64) {
	w.WriteLEB128Signed(v)
}

// WriteF32 writes a 32-bit floating point number.
func (w *ByteWriter) WriteF32(v float32) {
	var buf [4]byte
	binary.LittleEndian.PutUint32(buf[:], math.Float32bits(v))
	for i := range buf {
		w.WriteByte(buf[i])
	}
}

// WriteF64 writes a 64-bit floating point number.
func (w *ByteWriter) WriteF64(v float64) {
	var buf [8]byte
	binary.LittleEndian.PutUint64(buf[:], math.Float64bits(v))
	for i := range buf {
		w.WriteByte(buf[i])
	}
}

// WriteI128 writes a 128-bit value (for v128 constants).
func (w *ByteWriter) WriteI128(v [16]byte) {
	for i := range v {
		w.WriteByte(v[i])
	}
}

// WriteIndex writes an unsigned integer index value using LEB128 encoding.
func (w *ByteWriter) WriteIndex(v uint32) {
	w.WriteLEB128Unsigned(uint64(v))
}

// WriteLEB128Unsigned writes an unsigned integer in LEB128 format.
func (w *ByteWriter) WriteLEB128Unsigned(v uint64) {
	for {
		b := byte(v & 0x7f)
		v >>= 7
		if v != 0 {
			b |= 0x80
		}
		w.WriteByte(b)
		if v == 0 {
			break
		}
	}
}

// WriteLEB128Signed writes a signed integer in LEB128 format.
func (w *ByteWriter) WriteLEB128Signed(v int64) {
	more := true
	for more {
		b := byte(v & 0x7f)
		v >>= 7

		// Check if additional bytes are needed
		if (v == 0 && (b&0x40) == 0) || (v == -1 && (b&0x40) != 0) {
			more = false
		} else {
			b |= 0x80
		}

		w.WriteByte(b)
	}
}

// MemArg writes memory arguments (alignment and offset).
func (w *ByteWriter) MemArg(align, offset uint32) {
	w.WriteLEB128Unsigned(uint64(align))
	w.WriteLEB128Unsigned(uint64(offset))
}

// CodeAssembler wraps a Writer with higher-level methods for WebAssembly instructions.
type CodeAssembler struct {
	Writer
}

// NewCodeAssembler creates a new code assembler with a ByteWriter.
func NewCodeAssembler() *CodeAssembler {
	return &CodeAssembler{
		Writer: NewByteWriter(),
	}
}

// NewCodeAssemblerWithWriter creates a new code assembler with the given writer.
func NewCodeAssemblerWithWriter(w Writer) *CodeAssembler {
	return &CodeAssembler{
		Writer: w,
	}
}

// Bytes returns the assembled code if the underlying writer is a ByteWriter.
// Otherwise returns nil.
func (a *CodeAssembler) Bytes() []byte {
	if bw, ok := a.Writer.(*ByteWriter); ok {
		return bw.Bytes()
	}
	return nil
}

// Reset resets the underlying ByteWriter if possible.
func (a *CodeAssembler) Reset() {
	if bw, ok := a.Writer.(*ByteWriter); ok {
		bw.Reset()
	}
}
