package main

import (
	"encoding/csv"
	"fmt"
	"log"
	"os"
	"strings"
	"text/template"
)

// Instruction represents a WebAssembly instruction from the CSV file
type Instruction struct {
	Immediates  []string
	Opcode      string
	Signature   string
	MethodName  string
	ArgDefs     string
	OpcodeBytes string
}

const instructionTemplate = `
// {{ .Signature }}
func (a *CodeAssembler) {{ .MethodName }}({{ .ArgDefs }}) {
	{{ .OpcodeBytes }}
	{{- range $i, $imm := .Immediates }}
	{{- if eq $imm "memarg" }}
	a.MemArg(align, offset)
	{{- else if eq $imm "s_memarg" }}
	a.MemArg(align, offset)
	{{- else if eq $imm "u_memarg" }}
	a.MemArg(align, offset)
	{{- else if eq $imm "lane_memarg_laneidx" }}
	a.MemArg(align, offset)
	a.WriteByte(byte(lane))
	{{- else if eq $imm "splat_memarg" }}
	a.MemArg(align, offset)
	{{- else if eq $imm "zero_memarg" }}
	a.MemArg(align, offset)
	{{- else if eq $imm "i32" }}
	a.WriteI32(val)
	{{- else if eq $imm "i64" }}
	a.WriteI64(val)
	{{- else if eq $imm "f32" }}
	a.WriteF32(val)
	{{- else if eq $imm "f64" }}
	a.WriteF64(val)
	{{- else if eq $imm "i128" }}
	a.WriteI128(val)
	{{- else if eq $imm "laneidx" }}
	a.WriteByte(byte(lane))
	{{- else if eq $imm "s_laneidx" }}
	a.WriteByte(byte(lane))
	{{- else if eq $imm "u_laneidx" }}
	a.WriteByte(byte(lane))
	{{- else if eq $imm "laneidx{16}" }}
	for _, l := range lanes {
		a.WriteByte(byte(l))
	}
	{{- else if eq $imm "l" }}
	a.WriteIndex(label)
	{{- else if eq $imm "bt" }}
	a.WriteByte(byte(blocktype))
	{{- else if eq $imm "x" }}
	a.WriteIndex(idx)
	{{- else if eq $imm "y" }}
	a.WriteIndex(idx2)
	{{- else if eq $imm "t" }}
	a.WriteByte(byte(reftype))
	{{- else }}
	// Unsupported immediate type: {{ $imm }}
	{{- end }}
	{{- end }}
}
`

func main() {
	// Parse the CSV from stdin
	reader := csv.NewReader(os.Stdin)
	records, err := reader.ReadAll()
	if err != nil {
		log.Fatalf("Failed to read CSV: %v", err)
	}

	// Write header to stdout
	fmt.Println(`// Code generated by internal/cmd/codegen/main.go; DO NOT EDIT.

package webassembler

// Writer methods for WebAssembly instructions`)

	// Create template
	tmpl, err := template.New("instruction").Parse(instructionTemplate)
	if err != nil {
		log.Fatalf("Failed to parse template: %v", err)
	}

	// Process records and generate code
	for i, record := range records {
		// Skip header row
		if i == 0 {
			continue
		}

		// Get fields from CSV
		name := record[0]
		immediatesStr := record[1]
		opcode := record[2]

		// Skip empty or incomplete rows
		if name == "" || opcode == "" {
			continue
		}

		// Parse immediates
		var immediates []string
		if immediatesStr != "" {
			immediates = strings.Split(immediatesStr, ",")
		}

		// Parse stack effect.
		input := record[3]
		output := record[4]
		effect := formatStackEffect(input, output)

		// Create instruction object
		instr := Instruction{
			Immediates: immediates,
			Opcode:     opcode,
			MethodName: formatMethodName(name),
			Signature:  formatSignature(name, immediates, effect),
		}

		// Generate opcode bytes
		if strings.Contains(opcode, " ") {
			// Handle multi-byte opcodes (like FC 00, FD 01, etc.)
			parts := strings.Split(opcode, " ")
			opcodeHex := make([]string, len(parts))
			for i, part := range parts {
				opcodeHex[i] = "0x" + part
			}
			opcodeBytes := make([]string, len(parts))
			for i, part := range parts {
				opcodeBytes[i] = "a.WriteByte(0x" + part + ")"
			}
			instr.OpcodeBytes = strings.Join(opcodeBytes, "\n\t")
		} else {
			// Handle single-byte opcodes
			instr.OpcodeBytes = "a.WriteByte(0x" + opcode + ")"
		}

		// Generate argument definitions
		argDefs := []string{}
		for i, imm := range immediates {
			switch {
			case imm == "memarg", imm == "s_memarg", imm == "u_memarg",
				imm == "lane_memarg_laneidx", imm == "splat_memarg", imm == "zero_memarg":
				argDefs = append(argDefs, "align, offset uint32")
				if imm == "lane_memarg_laneidx" {
					argDefs = append(argDefs, "lane uint8")
				}
			case imm == "i32":
				argDefs = append(argDefs, "val int32")
			case imm == "i64":
				argDefs = append(argDefs, "val int64")
			case imm == "f32":
				argDefs = append(argDefs, "val float32")
			case imm == "f64":
				argDefs = append(argDefs, "val float64")
			case imm == "i128":
				argDefs = append(argDefs, "val [16]byte")
			case imm == "laneidx", imm == "s_laneidx", imm == "u_laneidx":
				argDefs = append(argDefs, "lane uint8")
			case imm == "laneidx{16}":
				argDefs = append(argDefs, "lanes [16]uint8")
			case imm == "l":
				if i == 0 {
					argDefs = append(argDefs, "label uint32")
				} else {
					argDefs = append(argDefs, fmt.Sprintf("label%d uint32", i+1))
				}
			case imm == "bt":
				argDefs = append(argDefs, "blocktype uint8")
			case imm == "x":
				argDefs = append(argDefs, "idx uint32")
			case imm == "y":
				argDefs = append(argDefs, "idx2 uint32")
			case imm == "t":
				argDefs = append(argDefs, "reftype uint8")
			default:
				argDefs = append(argDefs, fmt.Sprintf("arg%d %s", i+1, imm))
			}
		}
		instr.ArgDefs = strings.Join(argDefs, ", ")

		// Execute template to stdout
		err = tmpl.Execute(os.Stdout, instr)
		if err != nil {
			log.Fatalf("Failed to execute template for %s: %v", name, err)
		}
	}

}

func formatMethodName(instruction string) string {
	instruction = strings.ReplaceAll(instruction, ".", "._")
	parts := strings.Split(instruction, "_")
	method := ""
	for _, part := range parts {
		method += strings.ToUpper(string(part[0]))
		method += string(part[1:])
	}
	return strings.ReplaceAll(method, ".", "_")
}

func formatStackEffect(input string, output string) string {
	effect := ""
	if len(input) > 0 || len(output) > 0 {
		effect += "( "
		if len(input) > 0 {
			effect += input + " "
		}
		effect += "--"
		if len(output) > 0 {
			effect += " " + output
		}
		effect += " )"
		effect = strings.ReplaceAll(effect, ".", "_")
	}
	return effect
}

func formatSignature(name string, immediates []string, effect string) string {
	signature := name
	if len(immediates) > 0 {
		signature += " " + strings.Join(immediates, " ")
	}
	if len(effect) > 0 {
		signature += " " + effect
	}
	return signature
}
