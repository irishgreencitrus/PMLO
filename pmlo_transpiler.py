from pmlo_errors import pmlo_handler, pmlo_handle_except, PMLOFunctionNotFoundError

BRACKETS = "()"
C_PREFIX = "PMLO_Stack_"
class PMLOGenerateC:
    def __init__(self, tokens, outfile_path, base_file="transpiler/base.c"):
        self.all_tokens = list(tokens)
        self.base_file = base_file
        self.outfile_path = outfile_path
        self.code = None
        with open(base_file) as f:
            self.code = f.readlines()
            self.code = [x.strip() for x in self.code]
        self.registers = []
        self.max_scope = 0
        self.current_scope = 0
        self.labels = {}
        
        self.builtin_functions = {
            # Mathematical operators
            "+": "maths_add",
            "-": "maths_minus",
            "*": "maths_multiply",
            "pow": "maths_power",
            "/": "maths_divide",
            "%": "maths_modulo",
            "++": "maths_incr",
            "--": "maths_decr",
            # End mathematical operators

            # Base functions
            "!!": "core_reverse",
            # End base functions

            # Output functions
            "$": "output_dumpVal",
            "-$": "output_dumpValDestr",
            "$$": "output_dumpValStr",
            "-$$": "output_dumpValStrDestr",
            "$!": "output_dumpStack",
            "$$!": "output_dumpStackStr",
            # End output functions

            # "/$": self._pmlo_number_input,  # Input function
            # TODO(lime) add string input functions

            # Boolean operators
            "||": "bool_or",
            "&&": "bool_and",
            "!": "bool_not",

            "==": "equality_eq",
            "!=": "equality_neq",
            ">": "equality_gt",
            "<": "equality_lt",
            ">=": "equality_gt_eq",
            "<=": "equality_lt_eq",

            "~": "bitwise_not",
            "&": "bitwise_and",
            "|": "bitwise_or",
            "^": "bitwise_xor",
            "<<": "bitwise_lshift",
            ">>": "bitwise_rshift"
        }
        self._pmlo_find_notables()

    def _pmlo_find_notables(self):
        scope = 0
        for j, token in enumerate(self.all_tokens):
            if token.type == "OPEN_SCOPE":
                scope += 1
                if scope > self.max_scope:
                    self.max_scope = scope
            elif token.type == "CLOSE_SCOPE":
                scope -= 1
            elif token.type == "REGISTER_FUNCTION":
                register = token.value.split(BRACKETS[0])[1].strip(BRACKETS[1])
                if not (register in self.registers):
                    self.registers.append(register)

    def _pmlo_compile_token(self, token):
        if token.type == "NUMBER":
            self.code.append(f"PMLO_Stack_core_push(stack_{self.current_scope},{token.value});")
        elif token.type == "FUNCTION":
            if not (token.value in self.builtin_functions):
                with pmlo_handle_except(pmlo_handler):
                    raise PMLOFunctionNotFoundError(token.value) from None
            self.code.append(f"{C_PREFIX}{self.builtin_functions[token.value]}(stack_{self.current_scope});")
        elif token.type == "OPEN_SCOPE":
            self.current_scope += 1
            self.code.append(
                f"{C_PREFIX}new(stack_{self.current_scope}); // Scope number {self.current_scope} has opened")
        elif token.type == "CLOSE_SCOPE":
            self.code.append(
                f"{C_PREFIX}core_append(stack_{self.current_scope - 1},stack_{self.current_scope}); // Scope number {self.current_scope} has closed")
            self.current_scope -= 1
        elif token.type == "STRING":
            for i in token.value:
                self.code.append(
                    f"{C_PREFIX}push(stack_{self.current_scope},{ord(i)}); // Character '{i}' precompiled to number")
        elif token.type == "RANGE":
            start = int(token.value.split("..")[0])
            end = int(token.value.split("..")[1])
            self.code.append(
                f"for (int i = {start}; i <= {end}; i++) {C_PREFIX}core_push(stack_{self.current_scope}, i); // Range ({token.value}) compiled to for loop")
        elif token.type == "LABEL":
            self.code.append(f"{token.value}:")
        elif token.type == "LABEL_FUNCTION":
            fn = token.value.split(":")[0]
            label = token.value.split(":")[1]
            if fn == "jump":
                self.code.append(f"goto {label};")
            elif fn == "jump_if_not_zero":
                self.code.append(f"if ({C_PREFIX}core_getTop(stack_{self.current_scope}) != 0) goto {label};")
            elif fn == "jump_if_zero":
                self.code.append(f"if ({C_PREFIX}core_getTop(stack_{self.current_scope}) == 0) goto {label};")
            elif fn == "jump_if_stack_not_empty":
                self.code.append(f"if (! {C_PREFIX}core_isLength(stack_{self.current_scope}, 0)) goto {label};")
            elif fn == "jump_if_stack_empty":
                self.code.append(f"if ({C_PREFIX}core_isLength(stack_{self.current_scope}, 0)) goto {label};")
            elif fn == "jump_if_stack_one":
                self.code.append(f"if ({C_PREFIX}core_isLength(stack_{self.current_scope}, 1)) goto {label};")
            elif fn == "jump_if_stack_not_one":
                self.code.append(f"if (! {C_PREFIX}core_isLength(stack_{self.current_scope}, 1)) goto {label};")
        elif token.type == "REGISTER_FUNCTION":
            fn = token.value.split(BRACKETS[0])[0]
            register = token.value.split(BRACKETS[0])[1].strip(BRACKETS[1])
            if fn == "pop_into":
                self.code.append(f"register_{register} = {C_PREFIX}core_pop(stack_{self.current_scope});")
            elif fn == "copy_into":
                self.code.append(f"register_{register} = {C_PREFIX}core_getTop(stack_{self.current_scope});")
            elif fn == "pull_from":
                self.code.append(f"{C_PREFIX}core_push(stack_{self.current_scope},register_{register});")
            elif fn == "print":
                self.code.append(f'printf("%d\\n",register_{register})')
        elif token.type == "STACK_FUNCTION":
            fn = token.value.split(BRACKETS[0])[0]
            stack = token.value.split(BRACKETS[0])[1].strip(BRACKETS[1])
            if fn == "pop_into":
                self.code.append(
                    f"{C_PREFIX}core_push(stack_{stack}, {C_PREFIX}core_pop(stack_{self.current_scope}));")
            elif fn == "copy_into":
                self.code.append(
                    f"{C_PREFIX}core_push(stack_{stack}, {C_PREFIX}core_getTop(stack_{self.current_scope}));")
            elif fn == "pull_from":
                self.code.append(
                    f"{C_PREFIX}core_push(stack_{self.current_scope}, {C_PREFIX}core_pop(stack_{stack}));")
            elif fn == "print":
                self.code.append(f"{C_PREFIX}output_dumpStack(stack_{stack})")

    def start_compilation(self):
        self.code.append("int main() {")
        self.code.append("// Initialising used registers")
        for i in self.registers:
            self.code.append(f"STACK_DATA_TYPE register_{i} = 0;")
        self.code.append("// Finished initialising registers")
        for i in range(self.max_scope + 1):
            self.code.append(f"PMLO_Stack *stack_{i} = (PMLO_Stack *)malloc(sizeof(PMLO_Stack));")
            if i == 0:
                self.code.append(f"{C_PREFIX}new(stack_{i}); // Main stack has to be initialised here.")
        for i in self.all_tokens:
            self._pmlo_compile_token(i)
        self.code.append("}")
        with open(self.outfile_path,"w") as outfile:
            outfile.write("\n".join(self.code))

