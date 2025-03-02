package webassembler

type Module struct {
	Sections []Section

	Types TypeSection
	//Imports  Section
	Funcs FuncSection
	//Tables   Section
	//Memory   Section
	//Globals  Section
	Exports ExportSection
	//Starts   Section
	//Elements Section
	Code CodeSection
	//Data     Section
}

func NewModule() *Module {
	mod := &Module{}
	mod.Sections = []Section{
		&mod.Types,
		&mod.Funcs,
		&mod.Exports,
		&mod.Code,
	}
	return mod
}

func (mod *Module) Bytes() []byte {
	var buf Buffer
	mod.emit(&buf)
	return buf.Bytes()
}

func (mod *Module) emit(buf *Buffer) {
	mod.emitHeaders(buf)
	mod.emitSections(buf)
}

func (mod *Module) emitHeaders(buf *Buffer) {
	buf.WriteRaw([]byte{
		// Magic.
		0x00, 0x61, 0x73, 0x6D,
		// Version.
		0x01, 0x00, 0x00, 0x00,
	})
}

func (mod *Module) emitSections(buf *Buffer) {
	for _, s := range mod.Sections {
		writeSection(buf, s)
	}
}

func (mod *Module) ExportFunc(name string, idx FuncIdx) ExportIdx {
	return mod.Exports.AddFunc(name, idx)
}

func (mod *Module) AddFunc(typeIdx TypeIdx, code *Code) FuncIdx {
	funcIdx := mod.Funcs.Add(typeIdx)
	codeIdx := mod.Code.Add(code)
	if funcIdx != codeIdx {
		panic("misaligned function signatures and code sections")
	}
	return funcIdx
}
