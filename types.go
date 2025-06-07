package webassembler

type I32 = int32
type U32 = uint32
type I64 = int64
type U64 = uint64
type I128 = [16]byte
type F32 = float32
type F64 = float64
type LaneShuffle = [16]LaneIdx

type LaneIdx U32
type TypeIdx U32
type FuncIdx U32
type ExportIdx U32
type TableIdx U32
type MemIdx U32
type LabelIdx U32
type LocalIdx U32
type GlobalIdx U32

// Not part of the Webassembly spec.
type CodeIdx U32

func (idx LaneIdx) emit(buf *Buffer)   { buf.WriteU32(U32(idx)) }
func (idx TypeIdx) emit(buf *Buffer)   { buf.WriteU32(U32(idx)) }
func (idx FuncIdx) emit(buf *Buffer)   { buf.WriteU32(U32(idx)) }
func (idx LabelIdx) emit(buf *Buffer)  { buf.WriteU32(U32(idx)) }
func (idx LocalIdx) emit(buf *Buffer)  { buf.WriteU32(U32(idx)) }
func (idx GlobalIdx) emit(buf *Buffer) { buf.WriteU32(U32(idx)) }

type MemArg struct {
	Align  U32
	Offset U32
}

const (
	TypeI32       ValType = 0x7F
	TypeI64               = 0x7E
	TypeF32               = 0x7D
	TypeF64               = 0x7C
	TypeV128              = 0x7B
	TypeFuncRef           = 0x70
	TypeExternRef         = 0x6F
	TypeFunc              = 0x60
)

type ValType byte

func (typ ValType) emit(buf *Buffer) { buf.WriteValType(typ) }

type ResultType []ValType

func (rt ResultType) emit(buf *Buffer) {
	writeVec(buf, rt)
}

type TypeSection struct {
	n   U32
	buf Buffer
}

func (sec *TypeSection) SectionID() SectionID {
	return TypeSectionID
}

func (sec *TypeSection) Size() int {
	return unsignedLEB128Size(sec.n) + sec.buf.Len()
}

func (sec *TypeSection) emitContents(buf *Buffer) {
	buf.WriteU32(sec.n)
	buf.WriteRaw(sec.buf.Bytes())
}

func (sec *TypeSection) AddFunc(parameters, results ResultType) TypeIdx {
	idx := sec.n
	sec.n++
	sec.buf.WriteRawByte(0x60)
	parameters.emit(&sec.buf)
	results.emit(&sec.buf)
	return TypeIdx(idx)
}
