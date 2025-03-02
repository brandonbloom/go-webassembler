package webassembler

import "bytes"

type signed interface {
	I32 | I64
}

type unsigned interface {
	U32 | U64
}

func writeSignedLEB128[T signed](buf *bytes.Buffer, i T) {
	more := true
	for more {
		b := byte(i & 0x7f)
		i >>= 7

		if (i == 0 && (b&0x40) == 0) || (i == -1 && (b&0x40) != 0) {
			more = false
		} else {
			b |= 0x80
		}

		buf.WriteByte(b)
	}
}

func writeUnsignedLEB128[T unsigned](buf *bytes.Buffer, i T) {
	for {
		b := byte(i & 0x7f)
		i >>= 7
		if i != 0 {
			b |= 0x80
		}
		buf.WriteByte(b)
		if i == 0 {
			break
		}
	}
}
