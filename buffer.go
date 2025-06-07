package webassembler

import "bytes"

// A byte buffer extended with methods for writing WASM encodings.
type Buffer struct {
	buf bytes.Buffer
}

func (b *Buffer) Len() int {
	return b.buf.Len()
}

func (b *Buffer) Bytes() []byte {
	return b.buf.Bytes()
}

func (b *Buffer) WriteName(s string) {
	b.WriteU32(U32(len(s)))
	b.buf.WriteString(s)
}

func (b *Buffer) WriteRaw(bs []byte) {
	b.buf.Write(bs)
}

func (b *Buffer) WriteRawByte(c byte) {
	b.buf.WriteByte(c)
}

func (b *Buffer) WriteU32(i U32) {
	writeUnsignedLEB128(&b.buf, i)
}

func (b *Buffer) WriteI32(i I32) {
	writeSignedLEB128(&b.buf, i)
}

func (b *Buffer) WriteI64(i I64) {
	writeSignedLEB128(&b.buf, i)
}

func (b *Buffer) WriteF32(f F32) {
	panic("todo: WriteF32")
}

func (b *Buffer) WriteF64(f F64) {
	panic("todo: WriteF64")
}

func (b *Buffer) WriteI128(i I128) {
	panic("todo: WriteI128")
}

func (b *Buffer) WriteLaneShuffle(lanes LaneShuffle) {
	panic("todo: WriteLaneShuffle")
}

func (b *Buffer) WriteMemArg(mem MemArg) {
	b.WriteU32(mem.Align)
	b.WriteU32(mem.Offset)
}

func (b *Buffer) WriteTypeIdx(i TypeIdx) {
	b.WriteU32(U32(i))
}

func (b *Buffer) WriteLaneIdx(i LaneIdx) {
	b.WriteU32(U32(i))
}

func (b *Buffer) WriteLabelIdx(i LabelIdx) {
	b.WriteU32(U32(i))
}

func (b *Buffer) WriteLocalIdx(i LocalIdx) {
	b.WriteU32(U32(i))
}

func (b *Buffer) WriteGlobalIdx(i GlobalIdx) {
	b.WriteU32(U32(i))
}

func (b *Buffer) WriteFuncIdx(i FuncIdx) {
	b.WriteU32(U32(i))
}

func writeVec[T interface{ emit(*Buffer) }](buf *Buffer, xs []T) {
	buf.WriteU32(U32(len(xs)))
	for _, x := range xs {
		x.emit(buf)
	}
}

func (b *Buffer) WriteTableType(typ TableType) {
	b.WriteRefType(typ.RefType)
	b.WriteLimits(typ.Limits)
}

func (b *Buffer) WriteRefType(typ RefType) {
	b.WriteRawByte(byte(typ))
}

func (b *Buffer) WriteLimits(limits Limits) {
	if limits.IsUnlimited() {
		b.WriteRawByte(0x00)
		b.WriteU32(limits.Min)
	} else {
		b.WriteRawByte(0x01)
		b.WriteU32(limits.Min)
		b.WriteU32(limits.Max)
	}
}

func (b *Buffer) WriteMemType(typ MemType) {
	b.WriteLimits(typ.Limits)
}

func (b *Buffer) WriteGlobalType(typ GlobalType) {
	b.WriteValType(typ.Value)
	b.WriteBool(typ.Mutable)
}

func (b *Buffer) WriteValType(typ ValType) {
	b.WriteRawByte(byte(typ))
}

func (b *Buffer) WriteBool(value bool) {
	if value {
		b.WriteRawByte(1)
	} else {
		b.WriteRawByte(0)
	}
}
