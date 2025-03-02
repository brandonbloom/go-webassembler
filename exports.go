package webassembler

type ExportSection struct {
	n   int
	buf Buffer
}

func (sec *ExportSection) SectionID() SectionID {
	return ExportSectionID
}

func (sec *ExportSection) Bytes() []byte {
	return sec.buf.Bytes()
}

func (sec *ExportSection) add(name string, kind byte, idx U32) ExportIdx {
	export := sec.n
	sec.n++
	sec.buf.WriteName(name)
	sec.buf.WriteRawByte(kind)
	sec.buf.WriteU32(idx)
	return ExportIdx(export)
}

func (sec *ExportSection) AddFunc(name string, idx FuncIdx) ExportIdx {
	return sec.add(name, 0x00, U32(idx))
}

func (sec *ExportSection) AddTable(name string, idx TableIdx) ExportIdx {
	return sec.add(name, 0x01, U32(idx))
}

func (sec *ExportSection) AddMem(name string, idx MemIdx) ExportIdx {
	return sec.add(name, 0x02, U32(idx))
}

func (sec *ExportSection) AddGlobal(name string, idx GlobalIdx) ExportIdx {
	return sec.add(name, 0x03, U32(idx))
}
