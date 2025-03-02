package webassembler

type Code struct {
	buf Buffer
}

func NewCode(locals ...LocalType) *Code {
	c := &Code{}
	writeVec(&c.buf, locals)
	return c
}

type LocalType struct {
	N    U32
	Type TypeIdx
}

func (lt LocalType) emit(buf *Buffer) {
	buf.WriteU32(lt.N)
	lt.Type.emit(buf)
}

// The public interface of the Code object is made up of generated instruction methods.
//go:generate sh -c "go run internal/cmd/codegen/main.go <internal/instructions/index.csv >instructions.go"

type CodeSection struct {
	n     U32
	buf   Buffer
	funcs []*Code
}

func (sec *CodeSection) SectionID() SectionID {
	return CodeSectionID
}

func (sec *CodeSection) Size() int {
	return unsignedLEB128Size(sec.n) + sec.buf.Len()
}

func (sec *CodeSection) emitContents(buf *Buffer) {
	buf.WriteU32(sec.n)
	buf.WriteRaw(sec.buf.Bytes())
}

func (sec *CodeSection) Add(code *Code) FuncIdx {
	i := sec.n
	sec.n++
	sec.buf.WriteU32(U32(code.buf.Len()))
	sec.buf.WriteRaw(code.buf.Bytes())
	return FuncIdx(i)
}
