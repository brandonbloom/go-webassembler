package webassembler

type FuncSection struct {
	n   U32
	buf Buffer
}

func (sec *FuncSection) SectionID() SectionID {
	return FunctionSectionID
}

func (sec *FuncSection) Size() int {
	return unsignedLEB128Size(sec.n) + sec.buf.Len()
}

func (sec *FuncSection) emitContents(buf *Buffer) {
	buf.WriteU32(sec.n)
	buf.WriteRaw(sec.buf.Bytes())
}

func (sec *FuncSection) Add(typ TypeIdx) FuncIdx {
	i := sec.n
	sec.n++
	sec.buf.WriteTypeIdx(typ)
	return FuncIdx(i)
}
