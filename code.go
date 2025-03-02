// Package webassembler provides tools for generating WebAssembly binary code.
package webassembler

type Code struct {
	buf Buffer
}

func NewCode() *Code {
	return &Code{}
}

// The public interface of the Code object is made up of generated instruction methods.
//go:generate sh -c "go run internal/cmd/codegen/main.go <internal/instructions/index.csv >instructions.go"

type CodeSection struct {
	buf   Buffer
	funcs []*Code
}

type LocalTypes []LocalType

type LocalType struct {
	N    U32
	Type TypeIdx
}

func (lt LocalType) emit(buf *Buffer) {
	buf.WriteU32(lt.N)
	lt.Type.emit(buf)
}

func (sec *CodeSection) SectionID() SectionID {
	return CodeSectionID
}

func (sec *CodeSection) Bytes() []byte {
	return sec.buf.Bytes()
}

// When finished, must call .EndFunc() on result.
func (sec *CodeSection) BeginFunc(locals LocalTypes) *FuncCode {
	writeVec(&sec.buf, locals)
	return &FuncCode{
		buf: &sec.buf,
	}
}

type FuncCode struct {
	buf *Buffer
	Code
}

func (f *FuncCode) EndFunc() {
	f.buf.WriteU32(U32(f.Code.buf.Len()))
	f.buf.WriteRaw(f.Code.buf.Bytes())
}
