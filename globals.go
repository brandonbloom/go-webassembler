package webassembler

type GlobalType struct {
	Value   ValType
	Mutable bool
}

type GlobalSection struct {
	n   U32
	buf Buffer
}

func (sec *GlobalSection) SectionID() SectionID {
	return GlobalSectionID
}

func (sec *GlobalSection) Size() int {
	return unsignedLEB128Size(sec.n) + sec.buf.Len()
}

func (sec *GlobalSection) emitContents(buf *Buffer) {
	buf.WriteU32(sec.n)
	buf.WriteRaw(sec.buf.Bytes())
}

func (sec *GlobalSection) Add(typ GlobalType, numGlobalImports U32, code *Code) GlobalIdx {
	i := sec.n
	sec.n++
	sec.buf.WriteGlobalType(typ)
	sec.buf.WriteRaw(code.buf.Bytes())
	return GlobalIdx(numGlobalImports + i)
}
