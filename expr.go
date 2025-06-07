package webassembler

// Code provides an instruction encoder for an expression.
type Expr struct {
	buf Buffer
}

// The public interface of Expr is made up of generated instruction methods.
//go:generate sh -c "go run internal/cmd/codegen/main.go <internal/instructions/index.csv >instructions.go"
