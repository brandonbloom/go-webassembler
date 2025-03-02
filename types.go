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
	TypeI32       TypeIdx = 0x7F
	TypeI64               = 0x7E
	TypeF32               = 0x7D
	TypeF64               = 0x7C
	TypeV128              = 0x7B
	TypeFuncRef           = 0x70
	TypeExternRef         = 0x6F
	TypeFunc              = 0x60
)

type ResultType []TypeIdx

func (rt ResultType) emit(buf *Buffer) {
	writeVec(buf, rt)
}

type TypeSection struct {
	n   int
	buf Buffer
}

func (sec *TypeSection) SectionID() SectionID {
	return TypeSectionID
}

func (sec *TypeSection) Bytes() []byte {
	return sec.buf.Bytes()
}

func (sec *TypeSection) AddFunc(rt1, rt2 ResultType) TypeIdx {
	idx := sec.n
	sec.n++
	sec.buf.WriteRawByte(0x60)
	rt1.emit(&sec.buf)
	rt2.emit(&sec.buf)
	return TypeIdx(idx)
}
