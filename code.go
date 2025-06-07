package webassembler

// Code provides an instruction encoder encapsulating local variables with an expression.
type Code struct {
	Expr
}

func NewCode(locals ...LocalType) *Code {
	c := &Code{}
	// Abuses the internals of Expr to prefix with locals.
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

func (sec *CodeSection) Add(code *Code) CodeIdx {
	i := sec.n
	sec.n++
	sec.buf.WriteU32(U32(code.buf.Len()))
	sec.buf.WriteRaw(code.buf.Bytes())
	return CodeIdx(i)
}
