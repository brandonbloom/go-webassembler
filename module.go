package webassembler

type Module struct {
	Sections []Section

	Types   TypeSection
	Imports ImportSection
	Funcs   FuncSection
	//Tables   TableSection
	//Memory   MemorySection
	Globals GlobalSection
	Exports ExportSection
	//Starts   StartSection
	//Elements ElementSection
	Code CodeSection
	//Data     DataSection
}

func NewModule() *Module {
	mod := &Module{}
	mod.Sections = []Section{
		&mod.Types,
		&mod.Imports,
		&mod.Funcs,
		&mod.Globals,
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

func (mod *Module) ImportFunc(modName, name string, typ TypeIdx) FuncIdx {
	return mod.Imports.AddFunc(modName, name, typ)
}

func (mod *Module) ExportFunc(name string, idx FuncIdx) ExportIdx {
	return mod.Exports.AddFunc(name, idx)
}

func (mod *Module) AddFunc(typeIdx TypeIdx, code *Code) FuncIdx {
	mod.Imports.Freeze()
	numImports := mod.Imports.numFuncs
	funcIdx := mod.Funcs.Add(typeIdx, numImports)
	codeIdx := mod.Code.Add(code)
	if CodeIdx(int(funcIdx)-int(numImports)) != codeIdx {
		panic("misaligned function signatures and code sections")
	}
	return funcIdx
}

func (mod *Module) AddGlobal(globalType GlobalType, code *Code) GlobalIdx {
	mod.Imports.Freeze()
	numImports := mod.Imports.numGlobals
	return mod.Globals.Add(globalType, numImports, code)
}
