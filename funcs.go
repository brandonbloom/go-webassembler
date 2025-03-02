package webassembler

type FuncSection []TypeIdx

func (sec *FuncSection) SectionID() SectionID {
	return FunctionSectionID
}

func (sec *FuncSection) Bytes() []byte {
	var buf Buffer
	writeVec(&buf, *sec)
	return buf.Bytes()
}

func (sec *FuncSection) Add(typ TypeIdx) FuncIdx {
	f := len(*sec)
	*sec = append(*sec, typ)
	return FuncIdx(f)
}
