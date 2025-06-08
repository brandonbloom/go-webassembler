package webassembler

type MemType struct {
	Limits
}

type MemorySection struct {
	n   U32
	buf Buffer
}

func (sec *MemorySection) SectionID() SectionID {
	return MemorySectionID
}

func (sec *MemorySection) Size() int {
	return unsignedLEB128Size(sec.n) + sec.buf.Len()
}

func (sec *MemorySection) emitContents(buf *Buffer) {
	buf.WriteU32(sec.n)
	buf.WriteRaw(sec.buf.Bytes())
}

func (sec *MemorySection) Add(typ MemType, numMemoryImports U32) MemIdx {
	i := sec.n
	sec.n++
	sec.buf.WriteMemType(typ)
	return MemIdx(numMemoryImports + i)
}
