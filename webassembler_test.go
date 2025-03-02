package webassembler

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/tetratelabs/wazero"
)

func runInt(t *testing.T, mod *Module) int {
	ctx := t.Context()
	rt := wazero.NewRuntime(ctx)
	defer rt.Close(ctx)

	inst, err := rt.Instantiate(ctx, mod.Bytes())
	if err != nil {
		t.Fatalf("instantiating module: %v", err)
	}
	defer inst.Close(ctx)

	results, err := inst.ExportedFunction("_start").Call(ctx)
	if err != nil {
		t.Fatalf("calling _start: %v", err)
	}
	if len(results) != 1 {
		t.Fatalf("expected 1 result, got %d", len(results))
	}
	return int(results[0])
}

func TestWebassembler(t *testing.T) {
	mod := NewModule()

	typeIdx := mod.Types.AddFunc(nil, ResultType{TypeI32})

	code := NewCode()
	code.I32_Const(5)
	code.I32_Const(10)
	code.I32_Add()
	code.End()

	funcIdx := mod.AddFunc(typeIdx, code)
	_ = mod.ExportFunc("_start", funcIdx)

	// Uncomment to dump out files for debugging.
	//os.WriteFile("/tmp/dump.wasm", mod.Bytes(), 0600)

	res := runInt(t, mod)
	assert.Equal(t, 15, res)
}
