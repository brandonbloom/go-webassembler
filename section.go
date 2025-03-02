package webassembler

type SectionID byte

const (
	CustomSectionID    SectionID = 0
	TypeSectionID                = 1
	ImportSectionID              = 2
	FunctionSectionID            = 3
	TableSectionID               = 4
	MemorySectionID              = 5
	GlobalSectionID              = 6
	ExportSectionID              = 7
	StartSectionID               = 8
	ElementSectionID             = 9
	CodeSectionID                = 10
	DataSectionID                = 11
	DataCountSectionID           = 12
)

type Section interface {
	SectionID() SectionID
	Size() int
	emitContents(buf *Buffer)
}

func writeSection(buf *Buffer, s Section) {
	size := s.Size()
	if size == 0 {
		return
	}
	buf.WriteI32(I32(s.SectionID()))
	buf.WriteU32(U32(size))
	s.emitContents(buf)
}
