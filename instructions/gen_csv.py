# Adapted from https://github.com/WebAssembly/spec/blob/05949f507908aac3ad2a21661b5c39fa013da950/document/core/appendix/index-instructions.py
import csv
import re

def Instruction(name, opcode, type=None, validation=None, execution=None, operator=None):
    return (name, opcode, type, validation, execution)

def clean_opcode(opcode):
    # Remove \hex{} wrapper and strip 0x prefix
    opcode = re.sub(r'\\hex\{(0x)?([0-9A-F]+)\}', r'\2', opcode)
    # Replace ~~ with space in multi-byte opcodes
    opcode = opcode.replace('~~', ' ')
    # Replace ~ with space in multi-byte opcodes
    opcode = opcode.replace('~', ' ')
    return opcode

def clean_stack_notation(stack_notation):
    if stack_notation is None:
        return "", ""
    
    # Split the stack notation into input and output parts
    match = re.match(r'\[(.*?)\] \\to \[(.*?)\]', stack_notation)
    if match:
        input_part = match.group(1)
        output_part = match.group(2)
        
        # Clean LaTeX escape sequences
        input_part = re.sub(r'\\([A-Z][A-Z0-9]+)', r'\1', input_part)  # Change \I32 to I32
        input_part = input_part.replace('^\\ast', '[]')   
        input_part = input_part.replace('^\ast', '[]')
        input_part = input_part.replace('~', ',')
        input_part = re.sub(r'_[0-9]', '', input_part)  # Remove subscripts like _1, _2
        input_part = re.sub(r'\^', '', input_part)      # Remove remaining ^ symbols
        # Convert types to lowercase
        input_part = input_part.lower()
        
        output_part = re.sub(r'\\([A-Z][A-Z0-9]+)', r'\1', output_part)  # Change \I32 to I32
        output_part = output_part.replace('^\\ast', '[]')
        output_part = output_part.replace('^\ast', '[]')
        output_part = output_part.replace('~', ',')
        output_part = re.sub(r'_[0-9]', '', output_part)  # Remove subscripts
        output_part = re.sub(r'\^', '', output_part)      # Remove remaining ^ symbols
        # Convert types to lowercase
        output_part = output_part.lower()
        
        return input_part, output_part
    return "", ""

def clean_instruction_name(name):
    if name is None:
        return ""
    # Remove LaTeX commands and format nicely
    name = re.sub(r'\\([A-Z][A-Z0-9]*)', r'\1', name)  # Change \NOP to NOP
    name = name.replace('~', '_')
    name = re.sub(r'\\X\{([^}]+)\}', r'\1', name)  # Replace \X{bt} with bt
    name = re.sub(r'X\{([^}]+)\}', r'\1', name)     # Also handle without backslash
    name = re.sub(r'\\K\{([^}]+)\}', r'\1', name)   # Replace \K{\_s} with _s
    name = re.sub(r'K\{([^}]+)\}', r'\1', name)     # Also handle without backslash
    # Clean up any remaining escape sequences
    name = name.replace('\\', '')
    name = name.replace('\_', '_')
    name = re.sub(r'\^ast', '', name)  # Remove ^ast
    name = re.sub(r'\^', '', name)     # Remove any other ^
    # Convert to lowercase
    return name.lower()

def extract_immediates(name):
    """Extract immediates from instruction name."""
    if '_' not in name:
        return ""
    
    # Get everything after the first underscore
    parts = name.split('_', 1)
    if len(parts) > 1:
        # For compound immediates, replace some _ with .
        immediates = parts[1]
        
        # Handle sat_f32_s type patterns
        if 'sat_' in immediates:
            immediates = immediates.replace('_', '.')
        
        # Handle other compound patterns
        elif 'high_' in immediates or 'low_' in immediates:
            immediates = immediates.replace('_', '.')
        
        # Handle x_y type parameters
        elif len(immediates.split('_')) == 2 and all(len(p) == 1 for p in immediates.split('_')):
            immediates = immediates.replace('_', ',')
            
        return immediates
    return ""

def get_base_instruction(name):
    """Get the base instruction name without immediates."""
    if '_' not in name:
        return name
    
    # Get everything before the first underscore
    return name.split('_', 1)[0]

def generate_csv():
    with open('index.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['instruction', 'immediates', 'opcode', 'input', 'output'])
        
        for instr in INSTRUCTIONS:
            name, opcode, type_str, _, _ = instr
            
            # Skip rows with None (reserved) opcodes
            if name is None:
                continue
                
            clean_name = clean_instruction_name(name)
            base_instruction = get_base_instruction(clean_name)
            immediates = extract_immediates(clean_name)
            clean_code = clean_opcode(opcode)
            input_stack, output_stack = clean_stack_notation(type_str)
            
            writer.writerow([base_instruction, immediates, clean_code, input_stack, output_stack])


INSTRUCTIONS = [
    Instruction(r'\UNREACHABLE', r'\hex{00}', r'[t_1^\ast] \to [t_2^\ast]', r'valid-unreachable', r'exec-unreachable'),
    Instruction(r'\NOP', r'\hex{01}', r'[] \to []', r'valid-nop', r'exec-nop'),
    Instruction(r'\BLOCK~\X{bt}', r'\hex{02}', r'[t_1^\ast] \to [t_2^\ast]', r'valid-block', r'exec-block'),
    Instruction(r'\LOOP~\X{bt}', r'\hex{03}', r'[t_1^\ast] \to [t_2^\ast]', r'valid-loop', r'exec-loop'),
    Instruction(r'\IF~\X{bt}', r'\hex{04}', r'[t_1^\ast~\I32] \to [t_2^\ast]', r'valid-if', r'exec-if'),
    Instruction(r'\ELSE', r'\hex{05}'),
    Instruction(None, r'\hex{06}'),
    Instruction(None, r'\hex{07}'),
    Instruction(None, r'\hex{08}'),
    Instruction(None, r'\hex{09}'),
    Instruction(None, r'\hex{0A}'),
    Instruction(r'\END', r'\hex{0B}'),
    Instruction(r'\BR~l', r'\hex{0C}', r'[t_1^\ast~t^\ast] \to [t_2^\ast]', r'valid-br', r'exec-br'),
    Instruction(r'\BRIF~l', r'\hex{0D}', r'[t^\ast~\I32] \to [t^\ast]', r'valid-br_if', r'exec-br_if'),
    Instruction(r'\BRTABLE~l^\ast~l', r'\hex{0E}', r'[t_1^\ast~t^\ast~\I32] \to [t_2^\ast]', r'valid-br_table', r'exec-br_table'),
    Instruction(r'\RETURN', r'\hex{0F}', r'[t_1^\ast~t^\ast] \to [t_2^\ast]', r'valid-return', r'exec-return'),
    Instruction(r'\CALL~x', r'\hex{10}', r'[t_1^\ast] \to [t_2^\ast]', r'valid-call', r'exec-call'),
    Instruction(r'\CALLINDIRECT~x~y', r'\hex{11}', r'[t_1^\ast~\I32] \to [t_2^\ast]', r'valid-call_indirect', r'exec-call_indirect'),
    Instruction(None, r'\hex{12}'),
    Instruction(None, r'\hex{13}'),
    Instruction(None, r'\hex{14}'),
    Instruction(None, r'\hex{15}'),
    Instruction(None, r'\hex{16}'),
    Instruction(None, r'\hex{17}'),
    Instruction(None, r'\hex{18}'),
    Instruction(None, r'\hex{19}'),
    Instruction(r'\DROP', r'\hex{1A}', r'[t] \to []', r'valid-drop', r'exec-drop'),
    Instruction(r'\SELECT', r'\hex{1B}', r'[t~t~\I32] \to [t]', r'valid-select', r'exec-select'),
    Instruction(r'\SELECT~t', r'\hex{1C}', r'[t~t~\I32] \to [t]', r'valid-select', r'exec-select'),
    Instruction(None, r'\hex{1D}'),
    Instruction(None, r'\hex{1E}'),
    Instruction(None, r'\hex{1F}'),
    Instruction(r'\LOCALGET~x', r'\hex{20}', r'[] \to [t]', r'valid-local.get', r'exec-local.get'),
    Instruction(r'\LOCALSET~x', r'\hex{21}', r'[t] \to []', r'valid-local.set', r'exec-local.set'),
    Instruction(r'\LOCALTEE~x', r'\hex{22}', r'[t] \to [t]', r'valid-local.tee', r'exec-local.tee'),
    Instruction(r'\GLOBALGET~x', r'\hex{23}', r'[] \to [t]', r'valid-global.get', r'exec-global.get'),
    Instruction(r'\GLOBALSET~x', r'\hex{24}', r'[t] \to []', r'valid-global.set', r'exec-global.set'),
    Instruction(r'\TABLEGET~x', r'\hex{25}', r'[\I32] \to [t]', r'valid-table.get', r'exec-table.get'),
    Instruction(r'\TABLESET~x', r'\hex{26}', r'[\I32~t] \to []', r'valid-table.set', r'exec-table.set'),
    Instruction(None, r'\hex{27}'),
    Instruction(r'\I32.\LOAD~\memarg', r'\hex{28}', r'[\I32] \to [\I32]', r'valid-load', r'exec-load'),
    Instruction(r'\I64.\LOAD~\memarg', r'\hex{29}', r'[\I32] \to [\I64]', r'valid-load', r'exec-load'),
    Instruction(r'\F32.\LOAD~\memarg', r'\hex{2A}', r'[\I32] \to [\F32]', r'valid-load', r'exec-load'),
    Instruction(r'\F64.\LOAD~\memarg', r'\hex{2B}', r'[\I32] \to [\F64]', r'valid-load', r'exec-load'),
    Instruction(r'\I32.\LOAD\K{8\_s}~\memarg', r'\hex{2C}', r'[\I32] \to [\I32]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I32.\LOAD\K{8\_u}~\memarg', r'\hex{2D}', r'[\I32] \to [\I32]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I32.\LOAD\K{16\_s}~\memarg', r'\hex{2E}', r'[\I32] \to [\I32]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I32.\LOAD\K{16\_u}~\memarg', r'\hex{2F}', r'[\I32] \to [\I32]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I64.\LOAD\K{8\_s}~\memarg', r'\hex{30}', r'[\I32] \to [\I64]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I64.\LOAD\K{8\_u}~\memarg', r'\hex{31}', r'[\I32] \to [\I64]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I64.\LOAD\K{16\_s}~\memarg', r'\hex{32}', r'[\I32] \to [\I64]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I64.\LOAD\K{16\_u}~\memarg', r'\hex{33}', r'[\I32] \to [\I64]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I64.\LOAD\K{32\_s}~\memarg', r'\hex{34}', r'[\I32] \to [\I64]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I64.\LOAD\K{32\_u}~\memarg', r'\hex{35}', r'[\I32] \to [\I64]', r'valid-loadn', r'exec-loadn'),
    Instruction(r'\I32.\STORE~\memarg', r'\hex{36}', r'[\I32~\I32] \to []', r'valid-store', r'exec-store'),
    Instruction(r'\I64.\STORE~\memarg', r'\hex{37}', r'[\I32~\I64] \to []', r'valid-store', r'exec-store'),
    Instruction(r'\F32.\STORE~\memarg', r'\hex{38}', r'[\I32~\F32] \to []', r'valid-store', r'exec-store'),
    Instruction(r'\F64.\STORE~\memarg', r'\hex{39}', r'[\I32~\F64] \to []', r'valid-store', r'exec-store'),
    Instruction(r'\I32.\STORE\K{8}~\memarg', r'\hex{3A}', r'[\I32~\I32] \to []', r'valid-storen', r'exec-storen'),
    Instruction(r'\I32.\STORE\K{16}~\memarg', r'\hex{3B}', r'[\I32~\I32] \to []', r'valid-storen', r'exec-storen'),
    Instruction(r'\I64.\STORE\K{8}~\memarg', r'\hex{3C}', r'[\I32~\I64] \to []', r'valid-storen', r'exec-storen'),
    Instruction(r'\I64.\STORE\K{16}~\memarg', r'\hex{3D}', r'[\I32~\I64] \to []', r'valid-storen', r'exec-storen'),
    Instruction(r'\I64.\STORE\K{32}~\memarg', r'\hex{3E}', r'[\I32~\I64] \to []', r'valid-storen', r'exec-storen'),
    Instruction(r'\MEMORYSIZE', r'\hex{3F}', r'[] \to [\I32]', r'valid-memory.size', r'exec-memory.size'),
    Instruction(r'\MEMORYGROW', r'\hex{40}', r'[\I32] \to [\I32]', r'valid-memory.grow', r'exec-memory.grow'),
    Instruction(r'\I32.\CONST~\i32', r'\hex{41}', r'[] \to [\I32]', r'valid-const', r'exec-const'),
    Instruction(r'\I64.\CONST~\i64', r'\hex{42}', r'[] \to [\I64]', r'valid-const', r'exec-const'),
    Instruction(r'\F32.\CONST~\f32', r'\hex{43}', r'[] \to [\F32]', r'valid-const', r'exec-const'),
    Instruction(r'\F64.\CONST~\f64', r'\hex{44}', r'[] \to [\F64]', r'valid-const', r'exec-const'),
    Instruction(r'\I32.\EQZ', r'\hex{45}', r'[\I32] \to [\I32]', r'valid-testop', r'exec-testop', r'op-ieqz'),
    Instruction(r'\I32.\EQ', r'\hex{46}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ieq'),
    Instruction(r'\I32.\NE', r'\hex{47}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ine'),
    Instruction(r'\I32.\LT\K{\_s}', r'\hex{48}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ilt_s'),
    Instruction(r'\I32.\LT\K{\_u}', r'\hex{49}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ilt_u'),
    Instruction(r'\I32.\GT\K{\_s}', r'\hex{4A}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-igt_s'),
    Instruction(r'\I32.\GT\K{\_u}', r'\hex{4B}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-igt_u'),
    Instruction(r'\I32.\LE\K{\_s}', r'\hex{4C}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ile_s'),
    Instruction(r'\I32.\LE\K{\_u}', r'\hex{4D}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ile_u'),
    Instruction(r'\I32.\GE\K{\_s}', r'\hex{4E}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ige_s'),
    Instruction(r'\I32.\GE\K{\_u}', r'\hex{4F}', r'[\I32~\I32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ige_u'),
    Instruction(r'\I64.\EQZ', r'\hex{50}', r'[\I64] \to [\I32]', r'valid-testop', r'exec-testop', r'op-ieqz'),
    Instruction(r'\I64.\EQ', r'\hex{51}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ieq'),
    Instruction(r'\I64.\NE', r'\hex{52}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ine'),
    Instruction(r'\I64.\LT\K{\_s}', r'\hex{53}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ilt_s'),
    Instruction(r'\I64.\LT\K{\_u}', r'\hex{54}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ilt_u'),
    Instruction(r'\I64.\GT\K{\_s}', r'\hex{55}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-igt_s'),
    Instruction(r'\I64.\GT\K{\_u}', r'\hex{56}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-igt_u'),
    Instruction(r'\I64.\LE\K{\_s}', r'\hex{57}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ile_s'),
    Instruction(r'\I64.\LE\K{\_u}', r'\hex{58}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ile_u'),
    Instruction(r'\I64.\GE\K{\_s}', r'\hex{59}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ige_s'),
    Instruction(r'\I64.\GE\K{\_u}', r'\hex{5A}', r'[\I64~\I64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-ige_u'),
    Instruction(r'\F32.\EQ', r'\hex{5B}', r'[\F32~\F32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-feq'),
    Instruction(r'\F32.\NE', r'\hex{5C}', r'[\F32~\F32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fne'),
    Instruction(r'\F32.\LT', r'\hex{5D}', r'[\F32~\F32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-flt'),
    Instruction(r'\F32.\GT', r'\hex{5E}', r'[\F32~\F32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fgt'),
    Instruction(r'\F32.\LE', r'\hex{5F}', r'[\F32~\F32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fle'),
    Instruction(r'\F32.\GE', r'\hex{60}', r'[\F32~\F32] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fge'),
    Instruction(r'\F64.\EQ', r'\hex{61}', r'[\F64~\F64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-feq'),
    Instruction(r'\F64.\NE', r'\hex{62}', r'[\F64~\F64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fne'),
    Instruction(r'\F64.\LT', r'\hex{63}', r'[\F64~\F64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-flt'),
    Instruction(r'\F64.\GT', r'\hex{64}', r'[\F64~\F64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fgt'),
    Instruction(r'\F64.\LE', r'\hex{65}', r'[\F64~\F64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fle'),
    Instruction(r'\F64.\GE', r'\hex{66}', r'[\F64~\F64] \to [\I32]', r'valid-relop', r'exec-relop', r'op-fge'),
    Instruction(r'\I32.\CLZ', r'\hex{67}', r'[\I32] \to [\I32]', r'valid-unop', r'exec-unop', r'op-iclz'),
    Instruction(r'\I32.\CTZ', r'\hex{68}', r'[\I32] \to [\I32]', r'valid-unop', r'exec-unop', r'op-ictz'),
    Instruction(r'\I32.\POPCNT', r'\hex{69}', r'[\I32] \to [\I32]', r'valid-unop', r'exec-unop', r'op-ipopcnt'),
    Instruction(r'\I32.\ADD', r'\hex{6A}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-iadd'),
    Instruction(r'\I32.\SUB', r'\hex{6B}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-isub'),
    Instruction(r'\I32.\MUL', r'\hex{6C}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-imul'),
    Instruction(r'\I32.\DIV\K{\_s}', r'\hex{6D}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-idiv_s'),
    Instruction(r'\I32.\DIV\K{\_u}', r'\hex{6E}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-idiv_u'),
    Instruction(r'\I32.\REM\K{\_s}', r'\hex{6F}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-irem_s'),
    Instruction(r'\I32.\REM\K{\_u}', r'\hex{70}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-irem_u'),
    Instruction(r'\I32.\AND', r'\hex{71}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-iand'),
    Instruction(r'\I32.\OR', r'\hex{72}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-ior'),
    Instruction(r'\I32.\XOR', r'\hex{73}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-ixor'),
    Instruction(r'\I32.\SHL', r'\hex{74}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-ishl'),
    Instruction(r'\I32.\SHR\K{\_s}', r'\hex{75}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-ishr_s'),
    Instruction(r'\I32.\SHR\K{\_u}', r'\hex{76}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-ishr_u'),
    Instruction(r'\I32.\ROTL', r'\hex{77}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-irotl'),
    Instruction(r'\I32.\ROTR', r'\hex{78}', r'[\I32~\I32] \to [\I32]', r'valid-binop', r'exec-binop', r'op-irotr'),
    Instruction(r'\I64.\CLZ', r'\hex{79}', r'[\I64] \to [\I64]', r'valid-unop', r'exec-unop', r'op-iclz'),
    Instruction(r'\I64.\CTZ', r'\hex{7A}', r'[\I64] \to [\I64]', r'valid-unop', r'exec-unop', r'op-ictz'),
    Instruction(r'\I64.\POPCNT', r'\hex{7B}', r'[\I64] \to [\I64]', r'valid-unop', r'exec-unop', r'op-ipopcnt'),
    Instruction(r'\I64.\ADD', r'\hex{7C}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-iadd'),
    Instruction(r'\I64.\SUB', r'\hex{7D}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-isub'),
    Instruction(r'\I64.\MUL', r'\hex{7E}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-imul'),
    Instruction(r'\I64.\DIV\K{\_s}', r'\hex{7F}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-idiv_s'),
    Instruction(r'\I64.\DIV\K{\_u}', r'\hex{80}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-idiv_u'),
    Instruction(r'\I64.\REM\K{\_s}', r'\hex{81}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-irem_s'),
    Instruction(r'\I64.\REM\K{\_u}', r'\hex{82}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-irem_u'),
    Instruction(r'\I64.\AND', r'\hex{83}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-iand'),
    Instruction(r'\I64.\OR', r'\hex{84}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-ior'),
    Instruction(r'\I64.\XOR', r'\hex{85}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-ixor'),
    Instruction(r'\I64.\SHL', r'\hex{86}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-ishl'),
    Instruction(r'\I64.\SHR\K{\_s}', r'\hex{87}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-ishr_s'),
    Instruction(r'\I64.\SHR\K{\_u}', r'\hex{88}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-ishr_u'),
    Instruction(r'\I64.\ROTL', r'\hex{89}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-irotl'),
    Instruction(r'\I64.\ROTR', r'\hex{8A}', r'[\I64~\I64] \to [\I64]', r'valid-binop', r'exec-binop', r'op-irotr'),
    Instruction(r'\F32.\ABS', r'\hex{8B}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-fabs'),
    Instruction(r'\F32.\NEG', r'\hex{8C}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-fneg'),
    Instruction(r'\F32.\CEIL', r'\hex{8D}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-fceil'),
    Instruction(r'\F32.\FLOOR', r'\hex{8E}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-ffloor'),
    Instruction(r'\F32.\TRUNC', r'\hex{8F}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-ftrunc'),
    Instruction(r'\F32.\NEAREST', r'\hex{90}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-fnearest'),
    Instruction(r'\F32.\SQRT', r'\hex{91}', r'[\F32] \to [\F32]', r'valid-unop', r'exec-unop', r'op-fsqrt'),
    Instruction(r'\F32.\ADD', r'\hex{92}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fadd'),
    Instruction(r'\F32.\SUB', r'\hex{93}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fsub'),
    Instruction(r'\F32.\MUL', r'\hex{94}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fmul'),
    Instruction(r'\F32.\DIV', r'\hex{95}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fdiv'),
    Instruction(r'\F32.\FMIN', r'\hex{96}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fmin'),
    Instruction(r'\F32.\FMAX', r'\hex{97}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fmax'),
    Instruction(r'\F32.\COPYSIGN', r'\hex{98}', r'[\F32~\F32] \to [\F32]', r'valid-binop', r'exec-binop', r'op-fcopysign'),
    Instruction(r'\F64.\ABS', r'\hex{99}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-fabs'),
    Instruction(r'\F64.\NEG', r'\hex{9A}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-fneg'),
    Instruction(r'\F64.\CEIL', r'\hex{9B}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-fceil'),
    Instruction(r'\F64.\FLOOR', r'\hex{9C}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-ffloor'),
    Instruction(r'\F64.\TRUNC', r'\hex{9D}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-ftrunc'),
    Instruction(r'\F64.\NEAREST', r'\hex{9E}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-fnearest'),
    Instruction(r'\F64.\SQRT', r'\hex{9F}', r'[\F64] \to [\F64]', r'valid-unop', r'exec-unop', r'op-fsqrt'),
    Instruction(r'\F64.\ADD', r'\hex{A0}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fadd'),
    Instruction(r'\F64.\SUB', r'\hex{A1}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fsub'),
    Instruction(r'\F64.\MUL', r'\hex{A2}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fmul'),
    Instruction(r'\F64.\DIV', r'\hex{A3}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fdiv'),
    Instruction(r'\F64.\FMIN', r'\hex{A4}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fmin'),
    Instruction(r'\F64.\FMAX', r'\hex{A5}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fmax'),
    Instruction(r'\F64.\COPYSIGN', r'\hex{A6}', r'[\F64~\F64] \to [\F64]', r'valid-binop', r'exec-binop', r'op-fcopysign'),
    Instruction(r'\I32.\WRAP\K{\_}\I64', r'\hex{A7}', r'[\I64] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-wrap'),
    Instruction(r'\I32.\TRUNC\K{\_}\F32\K{\_s}', r'\hex{A8}', r'[\F32] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_s'),
    Instruction(r'\I32.\TRUNC\K{\_}\F32\K{\_u}', r'\hex{A9}', r'[\F32] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_u'),
    Instruction(r'\I32.\TRUNC\K{\_}\F64\K{\_s}', r'\hex{AA}', r'[\F64] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_s'),
    Instruction(r'\I32.\TRUNC\K{\_}\F64\K{\_u}', r'\hex{AB}', r'[\F64] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_u'),
    Instruction(r'\I64.\EXTEND\K{\_}\I32\K{\_s}', r'\hex{AC}', r'[\I32] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-extend_s'),
    Instruction(r'\I64.\EXTEND\K{\_}\I32\K{\_u}', r'\hex{AD}', r'[\I32] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-extend_u'),
    Instruction(r'\I64.\TRUNC\K{\_}\F32\K{\_s}', r'\hex{AE}', r'[\F32] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_s'),
    Instruction(r'\I64.\TRUNC\K{\_}\F32\K{\_u}', r'\hex{AF}', r'[\F32] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_u'),
    Instruction(r'\I64.\TRUNC\K{\_}\F64\K{\_s}', r'\hex{B0}', r'[\F64] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_s'),
    Instruction(r'\I64.\TRUNC\K{\_}\F64\K{\_u}', r'\hex{B1}', r'[\F64] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_u'),
    Instruction(r'\F32.\CONVERT\K{\_}\I32\K{\_s}', r'\hex{B2}', r'[\I32] \to [\F32]', r'valid-cvtop', r'exec-cvtop', r'op-convert_s'),
    Instruction(r'\F32.\CONVERT\K{\_}\I32\K{\_u}', r'\hex{B3}', r'[\I32] \to [\F32]', r'valid-cvtop', r'exec-cvtop', r'op-convert_u'),
    Instruction(r'\F32.\CONVERT\K{\_}\I64\K{\_s}', r'\hex{B4}', r'[\I64] \to [\F32]', r'valid-cvtop', r'exec-cvtop', r'op-convert_s'),
    Instruction(r'\F32.\CONVERT\K{\_}\I64\K{\_u}', r'\hex{B5}', r'[\I64] \to [\F32]', r'valid-cvtop', r'exec-cvtop', r'op-convert_u'),
    Instruction(r'\F32.\DEMOTE\K{\_}\F64', r'\hex{B6}', r'[\F64] \to [\F32]', r'valid-cvtop', r'exec-cvtop', r'op-demote'),
    Instruction(r'\F64.\CONVERT\K{\_}\I32\K{\_s}', r'\hex{B7}', r'[\I32] \to [\F64]', r'valid-cvtop', r'exec-cvtop', r'op-convert_s'),
    Instruction(r'\F64.\CONVERT\K{\_}\I32\K{\_u}', r'\hex{B8}', r'[\I32] \to [\F64]', r'valid-cvtop', r'exec-cvtop', r'op-convert_u'),
    Instruction(r'\F64.\CONVERT\K{\_}\I64\K{\_s}', r'\hex{B9}', r'[\I64] \to [\F64]', r'valid-cvtop', r'exec-cvtop', r'op-convert_s'),
    Instruction(r'\F64.\CONVERT\K{\_}\I64\K{\_u}', r'\hex{BA}', r'[\I64] \to [\F64]', r'valid-cvtop', r'exec-cvtop', r'op-convert_u'),
    Instruction(r'\F64.\PROMOTE\K{\_}\F32', r'\hex{BB}', r'[\F32] \to [\F64]', r'valid-cvtop', r'exec-cvtop', r'op-promote'),
    Instruction(r'\I32.\REINTERPRET\K{\_}\F32', r'\hex{BC}', r'[\F32] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-reinterpret'),
    Instruction(r'\I64.\REINTERPRET\K{\_}\F64', r'\hex{BD}', r'[\F64] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-reinterpret'),
    Instruction(r'\F32.\REINTERPRET\K{\_}\I32', r'\hex{BE}', r'[\I32] \to [\F32]', r'valid-cvtop', r'exec-cvtop', r'op-reinterpret'),
    Instruction(r'\F64.\REINTERPRET\K{\_}\I64', r'\hex{BF}', r'[\I64] \to [\F64]', r'valid-cvtop', r'exec-cvtop', r'op-reinterpret'),
    Instruction(r'\I32.\EXTEND\K{8\_s}', r'\hex{C0}', r'[\I32] \to [\I32]', r'valid-unop', r'exec-unop', r'op-iextendn_s'),
    Instruction(r'\I32.\EXTEND\K{16\_s}', r'\hex{C1}', r'[\I32] \to [\I32]', r'valid-unop', r'exec-unop', r'op-iextendn_s'),
    Instruction(r'\I64.\EXTEND\K{8\_s}', r'\hex{C2}', r'[\I64] \to [\I64]', r'valid-unop', r'exec-unop', r'op-iextendn_s'),
    Instruction(r'\I64.\EXTEND\K{16\_s}', r'\hex{C3}', r'[\I64] \to [\I64]', r'valid-unop', r'exec-unop', r'op-iextendn_s'),
    Instruction(r'\I64.\EXTEND\K{32\_s}', r'\hex{C4}', r'[\I64] \to [\I64]', r'valid-unop', r'exec-unop', r'op-iextendn_s'),
    Instruction(None, r'\hex{C5}'),
    Instruction(None, r'\hex{C6}'),
    Instruction(None, r'\hex{C7}'),
    Instruction(None, r'\hex{C8}'),
    Instruction(None, r'\hex{C9}'),
    Instruction(None, r'\hex{CA}'),
    Instruction(None, r'\hex{CB}'),
    Instruction(None, r'\hex{CC}'),
    Instruction(None, r'\hex{CD}'),
    Instruction(None, r'\hex{CE}'),
    Instruction(None, r'\hex{CF}'),
    Instruction(r'\REFNULL~t', r'\hex{D0}', r'[] \to [t]', r'valid-ref.null', r'exec-ref.null'),
    Instruction(r'\REFISNULL', r'\hex{D1}', r'[t] \to [\I32]', r'valid-ref.is_null', r'exec-ref.is_null'),
    Instruction(r'\REFFUNC~x', r'\hex{D2}', r'[] \to [\FUNCREF]', r'valid-ref.func', r'exec-ref.func'),
    Instruction(None, r'\hex{D3}'),
    Instruction(None, r'\hex{D4}'),
    Instruction(None, r'\hex{D5}'),
    Instruction(None, r'\hex{D6}'),
    Instruction(None, r'\hex{D7}'),
    Instruction(None, r'\hex{D8}'),
    Instruction(None, r'\hex{D9}'),
    Instruction(None, r'\hex{DA}'),
    Instruction(None, r'\hex{DB}'),
    Instruction(None, r'\hex{DC}'),
    Instruction(None, r'\hex{DD}'),
    Instruction(None, r'\hex{DE}'),
    Instruction(None, r'\hex{DF}'),
    Instruction(None, r'\hex{E0}'),
    Instruction(None, r'\hex{E1}'),
    Instruction(None, r'\hex{E2}'),
    Instruction(None, r'\hex{E3}'),
    Instruction(None, r'\hex{E4}'),
    Instruction(None, r'\hex{E5}'),
    Instruction(None, r'\hex{E6}'),
    Instruction(None, r'\hex{E7}'),
    Instruction(None, r'\hex{E8}'),
    Instruction(None, r'\hex{E9}'),
    Instruction(None, r'\hex{EA}'),
    Instruction(None, r'\hex{EB}'),
    Instruction(None, r'\hex{EC}'),
    Instruction(None, r'\hex{ED}'),
    Instruction(None, r'\hex{EE}'),
    Instruction(None, r'\hex{EF}'),
    Instruction(None, r'\hex{F0}'),
    Instruction(None, r'\hex{F1}'),
    Instruction(None, r'\hex{F2}'),
    Instruction(None, r'\hex{F3}'),
    Instruction(None, r'\hex{F4}'),
    Instruction(None, r'\hex{F5}'),
    Instruction(None, r'\hex{F6}'),
    Instruction(None, r'\hex{F7}'),
    Instruction(None, r'\hex{F8}'),
    Instruction(None, r'\hex{F9}'),
    Instruction(None, r'\hex{FA}'),
    Instruction(None, r'\hex{FB}'),
    Instruction(r'\I32.\TRUNC\K{\_sat\_}\F32\K{\_s}', r'\hex{FC}~\hex{00}', r'[\F32] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_s'),
    Instruction(r'\I32.\TRUNC\K{\_sat\_}\F32\K{\_u}', r'\hex{FC}~\hex{01}', r'[\F32] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_u'),
    Instruction(r'\I32.\TRUNC\K{\_sat\_}\F64\K{\_s}', r'\hex{FC}~\hex{02}', r'[\F64] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_s'),
    Instruction(r'\I32.\TRUNC\K{\_sat\_}\F64\K{\_u}', r'\hex{FC}~\hex{03}', r'[\F64] \to [\I32]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_u'),
    Instruction(r'\I64.\TRUNC\K{\_sat\_}\F32\K{\_s}', r'\hex{FC}~\hex{04}', r'[\F32] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_s'),
    Instruction(r'\I64.\TRUNC\K{\_sat\_}\F32\K{\_u}', r'\hex{FC}~\hex{05}', r'[\F32] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_u'),
    Instruction(r'\I64.\TRUNC\K{\_sat\_}\F64\K{\_s}', r'\hex{FC}~\hex{06}', r'[\F64] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_s'),
    Instruction(r'\I64.\TRUNC\K{\_sat\_}\F64\K{\_u}', r'\hex{FC}~\hex{07}', r'[\F64] \to [\I64]', r'valid-cvtop', r'exec-cvtop', r'op-trunc_sat_u'),
    Instruction(r'\MEMORYINIT~x', r'\hex{FC}~\hex{08}', r'[\I32~\I32~\I32] \to []', r'valid-memory.init', r'exec-memory.init'),
    Instruction(r'\DATADROP~x', r'\hex{FC}~\hex{09}', r'[] \to []', r'valid-data.drop', r'exec-data.drop'),
    Instruction(r'\MEMORYCOPY', r'\hex{FC}~\hex{0A}', r'[\I32~\I32~\I32] \to []', r'valid-memory.copy', r'exec-memory.copy'),
    Instruction(r'\MEMORYFILL', r'\hex{FC}~\hex{0B}', r'[\I32~\I32~\I32] \to []', r'valid-memory.fill', r'exec-memory.fill'),
    Instruction(r'\TABLEINIT~x~y', r'\hex{FC}~\hex{0C}', r'[\I32~\I32~\I32] \to []', r'valid-table.init', r'exec-table.init'),
    Instruction(r'\ELEMDROP~x', r'\hex{FC}~\hex{0D}', r'[] \to []', r'valid-elem.drop', r'exec-elem.drop'),
    Instruction(r'\TABLECOPY~x~y', r'\hex{FC}~\hex{0E}', r'[\I32~\I32~\I32] \to []', r'valid-table.copy', r'exec-table.copy'),
    Instruction(r'\TABLEGROW~x', r'\hex{FC}~\hex{0F}', r'[t~\I32] \to [\I32]', r'valid-table.grow', r'exec-table.grow'),
    Instruction(r'\TABLESIZE~x', r'\hex{FC}~\hex{10}', r'[] \to [\I32]', r'valid-table.size', r'exec-table.size'),
    Instruction(r'\TABLEFILL~x', r'\hex{FC}~\hex{11}', r'[\I32~t~\I32] \to []', r'valid-table.fill', r'exec-table.fill'),
    Instruction(r'\V128.\LOAD~\memarg', r'\hex{FD}~~\hex{00}', r'[\I32] \to [\V128]', r'valid-load', r'exec-load'),
    Instruction(r'\V128.\LOAD\K{8x8\_s}~\memarg', r'\hex{FD}~~\hex{01}', r'[\I32] \to [\V128]', r'valid-load-extend', r'exec-load-extend'),
    Instruction(r'\V128.\LOAD\K{8x8\_u}~\memarg', r'\hex{FD}~~\hex{02}', r'[\I32] \to [\V128]', r'valid-load-extend', r'exec-load-extend'),
    Instruction(r'\V128.\LOAD\K{16x4\_s}~\memarg', r'\hex{FD}~~\hex{03}', r'[\I32] \to [\V128]', r'valid-load-extend', r'exec-load-extend'),
    Instruction(r'\V128.\LOAD\K{16x4\_u}~\memarg', r'\hex{FD}~~\hex{04}', r'[\I32] \to [\V128]', r'valid-load-extend', r'exec-load-extend'),
    Instruction(r'\V128.\LOAD\K{32x2\_s}~\memarg', r'\hex{FD}~~\hex{05}', r'[\I32] \to [\V128]', r'valid-load-extend', r'exec-load-extend'),
    Instruction(r'\V128.\LOAD\K{32x2\_u}~\memarg', r'\hex{FD}~~\hex{06}', r'[\I32] \to [\V128]', r'valid-load-extend', r'exec-load-extend'),
    Instruction(r'\V128.\LOAD\K{8\_splat}~\memarg', r'\hex{FD}~~\hex{07}', r'[\I32] \to [\V128]', r'valid-load-splat', r'exec-load-splat'),
    Instruction(r'\V128.\LOAD\K{16\_splat}~\memarg', r'\hex{FD}~~\hex{08}', r'[\I32] \to [\V128]', r'valid-load-splat', r'exec-load-splat'),
    Instruction(r'\V128.\LOAD\K{32\_splat}~\memarg', r'\hex{FD}~~\hex{09}', r'[\I32] \to [\V128]', r'valid-load-splat', r'exec-load-splat'),
    Instruction(r'\V128.\LOAD\K{64\_splat}~\memarg', r'\hex{FD}~~\hex{0A}', r'[\I32] \to [\V128]', r'valid-load-splat', r'exec-load-splat'),
    Instruction(r'\V128.\STORE~\memarg', r'\hex{FD}~~\hex{0B}', r'[\I32~\V128] \to []', r'valid-store', r'exec-store'),
    Instruction(r'\V128.\VCONST~\i128', r'\hex{FD}~~\hex{0C}', r'[] \to [\V128]', r'valid-vconst', r'exec-vconst'),
    Instruction(r'\I8X16.\SHUFFLE~\laneidx^{16}', r'\hex{FD}~~\hex{0D}', r'[\V128~\V128] \to [\V128]', r'valid-vec-shuffle', r'exec-vec-shuffle'),
    Instruction(r'\I8X16.\SWIZZLE', r'\hex{FD}~~\hex{0E}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vec-swizzle'),
    Instruction(r'\I8X16.\SPLAT', r'\hex{FD}~~\hex{0F}', r'[\I32] \to [\V128]', r'valid-vec-splat', r'exec-vec-splat'),
    Instruction(r'\I16X8.\SPLAT', r'\hex{FD}~~\hex{10}', r'[\I32] \to [\V128]', r'valid-vec-splat', r'exec-vec-splat'),
    Instruction(r'\I32X4.\SPLAT', r'\hex{FD}~~\hex{11}', r'[\I32] \to [\V128]', r'valid-vec-splat', r'exec-vec-splat'),
    Instruction(r'\I64X2.\SPLAT', r'\hex{FD}~~\hex{12}', r'[\I64] \to [\V128]', r'valid-vec-splat', r'exec-vec-splat'),
    Instruction(r'\F32X4.\SPLAT', r'\hex{FD}~~\hex{13}', r'[\F32] \to [\V128]', r'valid-vec-splat', r'exec-vec-splat'),
    Instruction(r'\F64X2.\SPLAT', r'\hex{FD}~~\hex{14}', r'[\F64] \to [\V128]', r'valid-vec-splat', r'exec-vec-splat'),
    Instruction(r'\I8X16.\EXTRACTLANE\K{\_s}~\laneidx', r'\hex{FD}~~\hex{15}', r'[\V128] \to [\I32]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\I8X16.\EXTRACTLANE\K{\_u}~\laneidx', r'\hex{FD}~~\hex{16}', r'[\V128] \to [\I32]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\I8X16.\REPLACELANE~\laneidx', r'\hex{FD}~~\hex{17}', r'[\V128~\I32] \to [\V128]', r'valid-vec-replace_lane', r'exec-vec-replace_lane'),
    Instruction(r'\I16X8.\EXTRACTLANE\K{\_s}~\laneidx', r'\hex{FD}~~\hex{18}', r'[\V128] \to [\I32]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\I16X8.\EXTRACTLANE\K{\_u}~\laneidx', r'\hex{FD}~~\hex{19}', r'[\V128] \to [\I32]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\I16X8.\REPLACELANE~\laneidx', r'\hex{FD}~~\hex{1A}', r'[\V128~\I32] \to [\V128]', r'valid-vec-replace_lane', r'exec-vec-replace_lane'),
    Instruction(r'\I32X4.\EXTRACTLANE~\laneidx', r'\hex{FD}~~\hex{1B}', r'[\V128] \to [\I32]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\I32X4.\REPLACELANE~\laneidx', r'\hex{FD}~~\hex{1C}', r'[\V128~\I32] \to [\V128]', r'valid-vec-replace_lane', r'exec-vec-replace_lane'),
    Instruction(r'\I64X2.\EXTRACTLANE~\laneidx', r'\hex{FD}~~\hex{1D}', r'[\V128] \to [\I64]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\I64X2.\REPLACELANE~\laneidx', r'\hex{FD}~~\hex{1E}', r'[\V128~\I64] \to [\V128]', r'valid-vec-replace_lane', r'exec-vec-replace_lane'),
    Instruction(r'\F32X4.\EXTRACTLANE~\laneidx', r'\hex{FD}~~\hex{1F}', r'[\V128] \to [\F32]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\F32X4.\REPLACELANE~\laneidx', r'\hex{FD}~~\hex{20}', r'[\V128~\F32] \to [\V128]', r'valid-vec-replace_lane', r'exec-vec-replace_lane'),
    Instruction(r'\F64X2.\EXTRACTLANE~\laneidx', r'\hex{FD}~~\hex{21}', r'[\V128] \to [\F64]', r'valid-vec-extract_lane', r'exec-vec-extract_lane'),
    Instruction(r'\F64X2.\REPLACELANE~\laneidx', r'\hex{FD}~~\hex{22}', r'[\V128~\F64] \to [\V128]', r'valid-vec-replace_lane', r'exec-vec-replace_lane'),
    Instruction(r'\I8X16.\VEQ', r'\hex{FD}~~\hex{23}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ieq'),
    Instruction(r'\I8X16.\VNE', r'\hex{FD}~~\hex{24}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ine'),
    Instruction(r'\I8X16.\VLT\K{\_s}', r'\hex{FD}~~\hex{25}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ilt_s'),
    Instruction(r'\I8X16.\VLT\K{\_u}', r'\hex{FD}~~\hex{26}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ilt_u'),
    Instruction(r'\I8X16.\VGT\K{\_s}', r'\hex{FD}~~\hex{27}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-igt_s'),
    Instruction(r'\I8X16.\VGT\K{\_u}', r'\hex{FD}~~\hex{28}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-igt_u'),
    Instruction(r'\I8X16.\VLE\K{\_s}', r'\hex{FD}~~\hex{29}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ile_s'),
    Instruction(r'\I8X16.\VLE\K{\_u}', r'\hex{FD}~~\hex{2A}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ile_u'),
    Instruction(r'\I8X16.\VGE\K{\_s}', r'\hex{FD}~~\hex{2B}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ige_s'),
    Instruction(r'\I8X16.\VGE\K{\_u}', r'\hex{FD}~~\hex{2C}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ige_u'),
    Instruction(r'\I16X8.\VEQ', r'\hex{FD}~~\hex{2D}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ieq'),
    Instruction(r'\I16X8.\VNE', r'\hex{FD}~~\hex{2E}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ine'),
    Instruction(r'\I16X8.\VLT\K{\_s}', r'\hex{FD}~~\hex{2F}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ilt_s'),
    Instruction(r'\I16X8.\VLT\K{\_u}', r'\hex{FD}~~\hex{30}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ilt_u'),
    Instruction(r'\I16X8.\VGT\K{\_s}', r'\hex{FD}~~\hex{31}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-igt_s'),
    Instruction(r'\I16X8.\VGT\K{\_u}', r'\hex{FD}~~\hex{32}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-igt_u'),
    Instruction(r'\I16X8.\VLE\K{\_s}', r'\hex{FD}~~\hex{33}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ile_s'),
    Instruction(r'\I16X8.\VLE\K{\_u}', r'\hex{FD}~~\hex{34}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ile_u'),
    Instruction(r'\I16X8.\VGE\K{\_s}', r'\hex{FD}~~\hex{35}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ige_s'),
    Instruction(r'\I16X8.\VGE\K{\_u}', r'\hex{FD}~~\hex{36}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ige_u'),
    Instruction(r'\I32X4.\VEQ', r'\hex{FD}~~\hex{37}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ieq'),
    Instruction(r'\I32X4.\VNE', r'\hex{FD}~~\hex{38}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ine'),
    Instruction(r'\I32X4.\VLT\K{\_s}', r'\hex{FD}~~\hex{39}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ilt_s'),
    Instruction(r'\I32X4.\VLT\K{\_u}', r'\hex{FD}~~\hex{3A}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ilt_u'),
    Instruction(r'\I32X4.\VGT\K{\_s}', r'\hex{FD}~~\hex{3B}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-igt_s'),
    Instruction(r'\I32X4.\VGT\K{\_u}', r'\hex{FD}~~\hex{3C}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-igt_u'),
    Instruction(r'\I32X4.\VLE\K{\_s}', r'\hex{FD}~~\hex{3D}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ile_s'),
    Instruction(r'\I32X4.\VLE\K{\_u}', r'\hex{FD}~~\hex{3E}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ile_u'),
    Instruction(r'\I32X4.\VGE\K{\_s}', r'\hex{FD}~~\hex{3F}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ige_s'),
    Instruction(r'\I32X4.\VGE\K{\_u}', r'\hex{FD}~~\hex{40}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-ige_u'),
    Instruction(r'\F32X4.\VEQ', r'\hex{FD}~~\hex{41}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-feq'),
    Instruction(r'\F32X4.\VNE', r'\hex{FD}~~\hex{42}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fne'),
    Instruction(r'\F32X4.\VLT', r'\hex{FD}~~\hex{43}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-flt'),
    Instruction(r'\F32X4.\VGT', r'\hex{FD}~~\hex{44}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fgt'),
    Instruction(r'\F32X4.\VLE', r'\hex{FD}~~\hex{45}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fle'),
    Instruction(r'\F32X4.\VGE', r'\hex{FD}~~\hex{46}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fge'),
    Instruction(r'\F64X2.\VEQ', r'\hex{FD}~~\hex{47}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-feq'),
    Instruction(r'\F64X2.\VNE', r'\hex{FD}~~\hex{48}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fne'),
    Instruction(r'\F64X2.\VLT', r'\hex{FD}~~\hex{49}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-flt'),
    Instruction(r'\F64X2.\VGT', r'\hex{FD}~~\hex{4A}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fgt'),
    Instruction(r'\F64X2.\VLE', r'\hex{FD}~~\hex{4B}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fle'),
    Instruction(r'\F64X2.\VGE', r'\hex{FD}~~\hex{4C}', r'[\V128~\V128] \to [\V128]', r'valid-vrelop', r'exec-vrelop', r'op-fge'),
    Instruction(r'\V128.\VNOT', r'\hex{FD}~~\hex{4D}', r'[\V128] \to [\V128]', r'valid-vvunop', r'exec-vvunop', r'op-inot'),
    Instruction(r'\V128.\VAND', r'\hex{FD}~~\hex{4E}', r'[\V128~\V128] \to [\V128]', r'valid-vvbinop', r'exec-vvbinop', r'op-iand'),
    Instruction(r'\V128.\VANDNOT', r'\hex{FD}~~\hex{4F}', r'[\V128~\V128] \to [\V128]', r'valid-vvbinop', r'exec-vvbinop', r'op-iandnot'),
    Instruction(r'\V128.\VOR', r'\hex{FD}~~\hex{50}', r'[\V128~\V128] \to [\V128]', r'valid-vvbinop', r'exec-vvbinop', r'op-ior'),
    Instruction(r'\V128.\VXOR', r'\hex{FD}~~\hex{51}', r'[\V128~\V128] \to [\V128]', r'valid-vvbinop', r'exec-vvbinop', r'op-ixor'),
    Instruction(r'\V128.\BITSELECT', r'\hex{FD}~~\hex{52}', r'[\V128~\V128~\V128] \to [\V128]', r'valid-vvternop', r'exec-vvternop', r'op-ibitselect'),
    Instruction(r'\V128.\ANYTRUE', r'\hex{FD}~~\hex{53}', r'[\V128] \to [\I32]', r'valid-vvtestop', r'exec-vvtestop'),
    Instruction(r'\V128.\LOAD\K{8\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{54}', r'[\I32~\V128] \to [\V128]', r'valid-load-lane', r'exec-load-lane'),
    Instruction(r'\V128.\LOAD\K{16\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{55}', r'[\I32~\V128] \to [\V128]', r'valid-load-lane', r'exec-load-lane'),
    Instruction(r'\V128.\LOAD\K{32\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{56}', r'[\I32~\V128] \to [\V128]', r'valid-load-lane', r'exec-load-lane'),
    Instruction(r'\V128.\LOAD\K{64\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{57}', r'[\I32~\V128] \to [\V128]', r'valid-load-lane', r'exec-load-lane'),
    Instruction(r'\V128.\STORE\K{8\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{58}', r'[\I32~\V128] \to []', r'valid-store-lane', r'exec-store-lane'),
    Instruction(r'\V128.\STORE\K{16\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{59}', r'[\I32~\V128] \to []', r'valid-store-lane', r'exec-store-lane'),
    Instruction(r'\V128.\STORE\K{32\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{5A}', r'[\I32~\V128] \to []', r'valid-store-lane', r'exec-store-lane'),
    Instruction(r'\V128.\STORE\K{64\_lane}~\memarg~\laneidx', r'\hex{FD}~~\hex{5B}', r'[\I32~\V128] \to []', r'valid-store-lane', r'exec-store-lane'),
    Instruction(r'\V128.\LOAD\K{32\_zero}~\memarg', r'\hex{FD}~~\hex{5C}', r'[\I32] \to [\V128]', r'valid-load-zero', r'exec-load-zero'),
    Instruction(r'\V128.\LOAD\K{64\_zero}~\memarg', r'\hex{FD}~~\hex{5D}', r'[\I32] \to [\V128]', r'valid-load-zero', r'exec-load-zero'),
    Instruction(r'\F32X4.\VDEMOTE\K{\_f64x2\_zero}', r'\hex{FD}~~\hex{5E}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-demote'),
    Instruction(r'\F64X2.\VPROMOTE\K{\_low\_f32x4}', r'\hex{FD}~~\hex{5F}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-promote'),
    Instruction(r'\I8X16.\VABS', r'\hex{FD}~~\hex{60}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-iabs'),
    Instruction(r'\I8X16.\VNEG', r'\hex{FD}~~\hex{61}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ineg'),
    Instruction(r'\I8X16.\VPOPCNT', r'\hex{FD}~~\hex{62}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ipopcnt'),
    Instruction(r'\I8X16.\ALLTRUE', r'\hex{FD}~~\hex{63}', r'[\V128] \to [\I32]', r'valid-vtestop', r'exec-vtestop'),
    Instruction(r'\I8X16.\BITMASK', r'\hex{FD}~~\hex{64}', r'[\V128] \to [\I32]', r'valid-vec-bitmask', r'exec-vec-bitmask'),
    Instruction(r'\I8X16.\NARROW\K{\_i16x8\_s}', r'\hex{FD}~~\hex{65}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vec-narrow'),
    Instruction(r'\I8X16.\NARROW\K{\_i16x8\_u}', r'\hex{FD}~~\hex{66}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vec-narrow'),
    Instruction(r'\F32X4.\VCEIL', r'\hex{FD}~~\hex{67}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fceil'),
    Instruction(r'\F32X4.\VFLOOR', r'\hex{FD}~~\hex{68}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ffloor'),
    Instruction(r'\F32X4.\VTRUNC', r'\hex{FD}~~\hex{69}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ftrunc'),
    Instruction(r'\F32X4.\VNEAREST', r'\hex{FD}~~\hex{6A}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fnearest'),
    Instruction(r'\I8X16.\VSHL', r'\hex{FD}~~\hex{6B}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishl'),
    Instruction(r'\I8X16.\VSHR\K{\_s}', r'\hex{FD}~~\hex{6C}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_s'),
    Instruction(r'\I8X16.\VSHR\K{\_u}', r'\hex{FD}~~\hex{6D}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_u'),
    Instruction(r'\I8X16.\VADD', r'\hex{FD}~~\hex{6E}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd'),
    Instruction(r'\I8X16.\VADD\K{\_sat\_s}', r'\hex{FD}~~\hex{6F}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd_sat_s'),
    Instruction(r'\I8X16.\VADD\K{\_sat\_u}', r'\hex{FD}~~\hex{70}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd_sat_u'),
    Instruction(r'\I8X16.\VSUB', r'\hex{FD}~~\hex{71}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub'),
    Instruction(r'\I8X16.\VSUB\K{\_sat\_s}', r'\hex{FD}~~\hex{72}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub_sat_s'),
    Instruction(r'\I8X16.\VSUB\K{\_sat\_u}', r'\hex{FD}~~\hex{73}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub_sat_u'),
    Instruction(r'\F64X2.\VCEIL', r'\hex{FD}~~\hex{74}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fceil'),
    Instruction(r'\F64X2.\VFLOOR', r'\hex{FD}~~\hex{75}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ffloor'),
    Instruction(r'\I8X16.\VMIN\K{\_s}', r'\hex{FD}~~\hex{76}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imin_s'),
    Instruction(r'\I8X16.\VMIN\K{\_u}', r'\hex{FD}~~\hex{77}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imin_u'),
    Instruction(r'\I8X16.\VMAX\K{\_s}', r'\hex{FD}~~\hex{78}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imax_s'),
    Instruction(r'\I8X16.\VMAX\K{\_u}', r'\hex{FD}~~\hex{79}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imax_u'),
    Instruction(r'\F64X2.\VTRUNC', r'\hex{FD}~~\hex{7A}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ftrunc'),
    Instruction(r'\I8X16.\AVGR\K{\_u}', r'\hex{FD}~~\hex{7B}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iavgr_u'),
    Instruction(r'\I16X8.\EXTADDPAIRWISE\K{\_i8x16\_s}', r'\hex{FD}~~\hex{7C}', r'[\V128] \to [\V128]', r'valid-vec-extadd_pairwise', r'exec-vec-extadd_pairwise'),
    Instruction(r'\I16X8.\EXTADDPAIRWISE\K{\_i8x16\_u}', r'\hex{FD}~~\hex{7D}', r'[\V128] \to [\V128]', r'valid-vec-extadd_pairwise', r'exec-vec-extadd_pairwise'),
    Instruction(r'\I32X4.\EXTADDPAIRWISE\K{\_i16x8\_s}', r'\hex{FD}~~\hex{7E}', r'[\V128] \to [\V128]', r'valid-vec-extadd_pairwise', r'exec-vec-extadd_pairwise'),
    Instruction(r'\I32X4.\EXTADDPAIRWISE\K{\_i16x8\_u}', r'\hex{FD}~~\hex{7F}', r'[\V128] \to [\V128]', r'valid-vec-extadd_pairwise', r'exec-vec-extadd_pairwise'),
    Instruction(r'\I16X8.\VABS', r'\hex{FD}~~\hex{80}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-iabs'),
    Instruction(r'\I16X8.\VNEG', r'\hex{FD}~~\hex{81}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ineg'),
    Instruction(r'\I16X8.\Q15MULRSAT\K{\_s}', r'\hex{FD}~~\hex{82}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iq15mulrsat_s'),
    Instruction(r'\I16X8.\ALLTRUE', r'\hex{FD}~~\hex{83}~~\hex{01}', r'[\V128] \to [\I32]', r'valid-vtestop', r'exec-vtestop'),
    Instruction(r'\I16X8.\BITMASK', r'\hex{FD}~~\hex{84}~~\hex{01}', r'[\V128] \to [\I32]', r'valid-vec-bitmask', r'exec-vec-bitmask'),
    Instruction(r'\I16X8.\NARROW\K{\_i32x4\_s}', r'\hex{FD}~~\hex{85}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vec-narrow'),
    Instruction(r'\I16X8.\NARROW\K{\_i32x4\_u}', r'\hex{FD}~~\hex{86}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vec-narrow'),
    Instruction(r'\I16X8.\VEXTEND\K{\_low\_i8x16\_s}', r'\hex{FD}~~\hex{87}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I16X8.\VEXTEND\K{\_high\_i8x16\_s}', r'\hex{FD}~~\hex{88}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I16X8.\VEXTEND\K{\_low\_i8x16\_u}', r'\hex{FD}~~\hex{89}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I16X8.\VEXTEND\K{\_high\_i8x16\_u}', r'\hex{FD}~~\hex{8A}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I16X8.\VSHL', r'\hex{FD}~~\hex{8B}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishl'),
    Instruction(r'\I16X8.\VSHR\K{\_s}', r'\hex{FD}~~\hex{8C}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_s'),
    Instruction(r'\I16X8.\VSHR\K{\_u}', r'\hex{FD}~~\hex{8D}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_u'),
    Instruction(r'\I16X8.\VADD', r'\hex{FD}~~\hex{8E}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd'),
    Instruction(r'\I16X8.\VADD\K{\_sat\_s}', r'\hex{FD}~~\hex{8F}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd_sat_s'),
    Instruction(r'\I16X8.\VADD\K{\_sat\_u}', r'\hex{FD}~~\hex{90}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd_sat_u'),
    Instruction(r'\I16X8.\VSUB', r'\hex{FD}~~\hex{91}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub'),
    Instruction(r'\I16X8.\VSUB\K{\_sat\_s}', r'\hex{FD}~~\hex{92}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub_sat_s'),
    Instruction(r'\I16X8.\VSUB\K{\_sat\_u}', r'\hex{FD}~~\hex{93}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub_sat_u'),
    Instruction(r'\F64X2.\VNEAREST', r'\hex{FD}~~\hex{94}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fnearest'),
    Instruction(r'\I16X8.\VMUL', r'\hex{FD}~~\hex{95}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imul'),
    Instruction(r'\I16X8.\VMIN\K{\_s}', r'\hex{FD}~~\hex{96}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imin_s'),
    Instruction(r'\I16X8.\VMIN\K{\_u}', r'\hex{FD}~~\hex{97}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imin_u'),
    Instruction(r'\I16X8.\VMAX\K{\_s}', r'\hex{FD}~~\hex{98}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imax_s'),
    Instruction(r'\I16X8.\VMAX\K{\_u}', r'\hex{FD}~~\hex{99}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imax_u'),
    Instruction(r'\I16X8.\AVGR\K{\_u}', r'\hex{FD}~~\hex{9B}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iavgr_u'),
    Instruction(r'\I16X8.\EXTMUL\K{\_low\_i8x16\_s}', r'\hex{FD}~~\hex{9C}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I16X8.\EXTMUL\K{\_high\_i8x16\_s}', r'\hex{FD}~~\hex{9D}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I16X8.\EXTMUL\K{\_low\_i8x16\_u}', r'\hex{FD}~~\hex{9E}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I16X8.\EXTMUL\K{\_high\_i8x16\_u}', r'\hex{FD}~~\hex{9F}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I32X4.\VABS', r'\hex{FD}~~\hex{A0}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-iabs'),
    Instruction(r'\I32X4.\VNEG', r'\hex{FD}~~\hex{A1}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ineg'),
    Instruction(r'\I32X4.\ALLTRUE', r'\hex{FD}~~\hex{A3}~~\hex{01}', r'[\V128] \to [\I32]', r'valid-vtestop', r'exec-vtestop'),
    Instruction(r'\I32X4.\BITMASK', r'\hex{FD}~~\hex{A4}~~\hex{01}', r'[\V128] \to [\I32]', r'valid-vec-bitmask', r'exec-vec-bitmask'),
    Instruction(r'\I32X4.\VEXTEND\K{\_low\_i16x8\_s}', r'\hex{FD}~~\hex{A7}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I32X4.\VEXTEND\K{\_high\_i16x8\_s}', r'\hex{FD}~~\hex{A8}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I32X4.\VEXTEND\K{\_low\_i16x8\_u}', r'\hex{FD}~~\hex{A9}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I32X4.\VEXTEND\K{\_high\_i16x8\_u}', r'\hex{FD}~~\hex{AA}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I32X4.\VSHL', r'\hex{FD}~~\hex{AB}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishl'),
    Instruction(r'\I32X4.\VSHR\K{\_s}', r'\hex{FD}~~\hex{AC}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_s'),
    Instruction(r'\I32X4.\VSHR\K{\_u}', r'\hex{FD}~~\hex{AD}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_u'),
    Instruction(r'\I32X4.\VADD', r'\hex{FD}~~\hex{AE}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd'),
    Instruction(r'\I32X4.\VSUB', r'\hex{FD}~~\hex{B1}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub'),
    Instruction(r'\I32X4.\VMUL', r'\hex{FD}~~\hex{B5}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imul'),
    Instruction(r'\I32X4.\VMIN\K{\_s}', r'\hex{FD}~~\hex{B6}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imin_s'),
    Instruction(r'\I32X4.\VMIN\K{\_u}', r'\hex{FD}~~\hex{B7}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imin_u'),
    Instruction(r'\I32X4.\VMAX\K{\_s}', r'\hex{FD}~~\hex{B8}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imax_s'),
    Instruction(r'\I32X4.\VMAX\K{\_u}', r'\hex{FD}~~\hex{B9}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imax_u'),
    Instruction(r'\I32X4.\DOT\K{\_i16x8\_s}', r'\hex{FD}~~\hex{BA}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-dot', r'exec-vec-dot'),
    Instruction(r'\I32X4.\EXTMUL\K{\_low\_i16x8\_s}', r'\hex{FD}~~\hex{BC}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I32X4.\EXTMUL\K{\_high\_i16x8\_s}', r'\hex{FD}~~\hex{BD}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I32X4.\EXTMUL\K{\_low\_i16x8\_u}', r'\hex{FD}~~\hex{BE}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I32X4.\EXTMUL\K{\_high\_i16x8\_u}', r'\hex{FD}~~\hex{BF}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I64X2.\VABS', r'\hex{FD}~~\hex{C0}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-iabs'),
    Instruction(r'\I64X2.\VNEG', r'\hex{FD}~~\hex{C1}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-ineg'),
    Instruction(r'\I64X2.\ALLTRUE', r'\hex{FD}~~\hex{C3}~~\hex{01}', r'[\V128] \to [\I32]', r'valid-vtestop', r'exec-vtestop'),
    Instruction(r'\I64X2.\BITMASK', r'\hex{FD}~~\hex{C4}~~\hex{01}', r'[\V128] \to [\I32]', r'valid-vec-bitmask', r'exec-vec-bitmask'),
    Instruction(r'\I64X2.\VEXTEND\K{\_low\_i32x4\_s}', r'\hex{FD}~~\hex{C7}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I64X2.\VEXTEND\K{\_high\_i32x4\_s}', r'\hex{FD}~~\hex{C8}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I64X2.\VEXTEND\K{\_low\_i32x4\_u}', r'\hex{FD}~~\hex{C9}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I64X2.\VEXTEND\K{\_high\_i32x4\_u}', r'\hex{FD}~~\hex{CA}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vcvtop'),
    Instruction(r'\I64X2.\VSHL', r'\hex{FD}~~\hex{CB}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishl'),
    Instruction(r'\I64X2.\VSHR\K{\_s}', r'\hex{FD}~~\hex{CC}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_s'),
    Instruction(r'\I64X2.\VSHR\K{\_u}', r'\hex{FD}~~\hex{CD}~~\hex{01}', r'[\V128~\I32] \to [\V128]', r'valid-vishiftop', r'exec-vishiftop', r'op-ishr_u'),
    Instruction(r'\I64X2.\VADD', r'\hex{FD}~~\hex{CE}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-iadd'),
    Instruction(r'\I64X2.\VSUB', r'\hex{FD}~~\hex{D1}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-isub'),
    Instruction(r'\I64X2.\VMUL', r'\hex{FD}~~\hex{D5}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-imul'),
    Instruction(r'\I64X2.\VEQ', r'\hex{FD}~~\hex{D6}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-ieq'),
    Instruction(r'\I64X2.\VNE', r'\hex{FD}~~\hex{D7}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-ine'),
    Instruction(r'\I64X2.\VLT\K{\_s}', r'\hex{FD}~~\hex{D8}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-ilt_s'),
    Instruction(r'\I64X2.\VGT\K{\_s}', r'\hex{FD}~~\hex{D9}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-igt_s'),
    Instruction(r'\I64X2.\VLE\K{\_s}', r'\hex{FD}~~\hex{DA}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-ile_s'),
    Instruction(r'\I64X2.\VGE\K{\_s}', r'\hex{FD}~~\hex{DB}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-ige_s'),
    Instruction(r'\I64X2.\EXTMUL\K{\_low\_i32x4\_s}', r'\hex{FD}~~\hex{DC}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I64X2.\EXTMUL\K{\_high\_i32x4\_s}', r'\hex{FD}~~\hex{DD}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I64X2.\EXTMUL\K{\_low\_i32x4\_u}', r'\hex{FD}~~\hex{DE}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\I64X2.\EXTMUL\K{\_high\_i32x4\_u}', r'\hex{FD}~~\hex{DF}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vec-extmul', r'exec-vec-extmul'),
    Instruction(r'\F32X4.\VABS', r'\hex{FD}~~\hex{E0}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fabs'),
    Instruction(r'\F32X4.\VNEG', r'\hex{FD}~~\hex{E1}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fneg'),
    Instruction(r'\F32X4.\VSQRT', r'\hex{FD}~~\hex{E3}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fsqrt'),
    Instruction(r'\F32X4.\VADD', r'\hex{FD}~~\hex{E4}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fadd'),
    Instruction(r'\F32X4.\VSUB', r'\hex{FD}~~\hex{E5}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fsub'),
    Instruction(r'\F32X4.\VMUL', r'\hex{FD}~~\hex{E6}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fmul'),
    Instruction(r'\F32X4.\VDIV', r'\hex{FD}~~\hex{E7}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fdiv'),
    Instruction(r'\F32X4.\VMIN', r'\hex{FD}~~\hex{E8}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fmin'),
    Instruction(r'\F32X4.\VMAX', r'\hex{FD}~~\hex{E9}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fmax'),
    Instruction(r'\F32X4.\VPMIN', r'\hex{FD}~~\hex{EA}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fpmin'),
    Instruction(r'\F32X4.\VPMAX', r'\hex{FD}~~\hex{EB}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fpmax'),
    Instruction(r'\F64X2.\VABS', r'\hex{FD}~~\hex{EC}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fabs'),
    Instruction(r'\F64X2.\VNEG', r'\hex{FD}~~\hex{ED}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fneg'),
    Instruction(r'\F64X2.\VSQRT', r'\hex{FD}~~\hex{EF}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vunop', r'exec-vunop', r'op-fsqrt'),
    Instruction(r'\F64X2.\VADD', r'\hex{FD}~~\hex{F0}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fadd'),
    Instruction(r'\F64X2.\VSUB', r'\hex{FD}~~\hex{F1}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fsub'),
    Instruction(r'\F64X2.\VMUL', r'\hex{FD}~~\hex{F2}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fmul'),
    Instruction(r'\F64X2.\VDIV', r'\hex{FD}~~\hex{F3}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fdiv'),
    Instruction(r'\F64X2.\VMIN', r'\hex{FD}~~\hex{F4}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fmin'),
    Instruction(r'\F64X2.\VMAX', r'\hex{FD}~~\hex{F5}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fmax'),
    Instruction(r'\F64X2.\VPMIN', r'\hex{FD}~~\hex{F6}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fpmin'),
    Instruction(r'\F64X2.\VPMAX', r'\hex{FD}~~\hex{F7}~~\hex{01}', r'[\V128~\V128] \to [\V128]', r'valid-vbinop', r'exec-vbinop', r'op-fpmax'),
    Instruction(r'\I32X4.\TRUNC\K{\_sat\_f32x4\_s}', r'\hex{FD}~~\hex{F8}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-trunc_sat_s'),
    Instruction(r'\I32X4.\TRUNC\K{\_sat\_f32x4\_u}', r'\hex{FD}~~\hex{F9}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-trunc_sat_u'),
    Instruction(r'\F32X4.\VCONVERT\K{\_i32x4\_s}', r'\hex{FD}~~\hex{FA}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-convert_s'),
    Instruction(r'\F32X4.\VCONVERT\K{\_i32x4\_u}', r'\hex{FD}~~\hex{FB}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-convert_u'),
    Instruction(r'\I32X4.\VTRUNC\K{\_sat\_f64x2\_s\_zero}', r'\hex{FD}~~\hex{FC}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-trunc_sat_s'),
    Instruction(r'\I32X4.\VTRUNC\K{\_sat\_f64x2\_u\_zero}', r'\hex{FD}~~\hex{FD}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-trunc_sat_u'),
    Instruction(r'\F64X2.\VCONVERT\K{\_low\_i32x4\_s}', r'\hex{FD}~~\hex{FE}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-convert_s'),
    Instruction(r'\F64X2.\VCONVERT\K{\_low\_i32x4\_u}', r'\hex{FD}~~\hex{FF}~~\hex{01}', r'[\V128] \to [\V128]', r'valid-vcvtop', r'exec-vcvtop', r'op-convert_u'),
]

# Generate the CSV file
if __name__ == "__main__":
    generate_csv()
