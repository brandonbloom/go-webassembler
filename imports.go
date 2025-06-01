package webassembler

type ImportSection struct {
	n   U32
	buf Buffer

	// The index space for functions, tables, memories and globals
	// includes respective imports declared in the same module.
	// The indices of these imports precede the indices of other
	// definitions in the same index space.
	numFuncs, numTables, numMemories, numGlobals U32

	// Prevents further imports when true. Forces entries in other
	// sections to be added only after their respective imports have
	// finished shifted the corresponding index space.
	frozen bool
}

func (sec *ImportSection) SectionID() SectionID {
	return ImportSectionID
}

func (sec *ImportSection) Size() int {
	return unsignedLEB128Size(sec.n) + sec.buf.Len()
}

func (sec *ImportSection) emitContents(buf *Buffer) {
	buf.WriteU32(sec.n)
	buf.WriteRaw(sec.buf.Bytes())
}

func (sec *ImportSection) Freeze() {
	sec.frozen = true
}

func (sec *ImportSection) AddFunc(mod, name string, typ TypeIdx) FuncIdx {
	idx := FuncIdx(sec.addImport(mod, name, 0x00, &sec.numFuncs))
	sec.buf.WriteTypeIdx(typ)
	return idx
}

func (sec *ImportSection) AddTable(mod, name string, typ TableType) TableIdx {
	idx := TableIdx(sec.addImport(mod, name, 0x01, &sec.numTables))
	sec.buf.WriteTableType(typ)
	return idx
}

func (sec *ImportSection) AddMemory(mod, name string, typ MemType) MemIdx {
	idx := MemIdx(sec.addImport(mod, name, 0x02, &sec.numMemories))
	sec.buf.WriteMemType(typ)
	return idx
}

func (sec *ImportSection) AddGlobal(mod, name string, typ GlobalType) GlobalIdx {
	idx := GlobalIdx(sec.addImport(mod, name, 0x03, &sec.numGlobals))
	sec.buf.WriteGlobalType(typ)
	return idx
}

func (sec *ImportSection) addImport(mod, name string, kind byte, num *U32) U32 {
	if sec.frozen {
		panic("imports are frozen")
	}

	idx := *num
	*num = idx + 1
	sec.n += 1

	sec.buf.WriteName(mod)
	sec.buf.WriteName(name)
	sec.buf.WriteRawByte(kind)

	return idx
}
