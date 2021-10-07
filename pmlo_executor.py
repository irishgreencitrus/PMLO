from collections import deque
from pmlo_errors import PMLOLabelNotFoundError, pmlo_handler, pmlo_handle_except


# TODO(lime) add REPL for PMLO
class PMLOExec:
    def __init__(self):
        self.stacks = [deque(maxlen=65535)]
        self.stack_pointer = 0
        self.labels = {}
        self.all_tokens = None
        self.code_pointer = 0
        self.registers = {}
        self.builtin_functions = {
            # Mathematical operators TODO(lime) require include
            "+": self._pmlo_add,
            "-": self._pmlo_subtract,
            "*": self._pmlo_multiply,
            "pow": self._pmlo_power,
            "/": self._pmlo_divide,
            "%": self._pmlo_modulo,
            "++": self._pmlo_incr,
            "--": self._pmlo_decr,
            # End mathematical operators

            # Base functions
            "!!": self._pmlo_stack_revr,
            # End base functions

            # Output functions TODO(lime) require include
            "$": self._pmlo_value_dump,
            "-$": self._pmlo_value_dump_destr,
            "$$": self._pmlo_value_dump_str,
            "-$$": self._pmlo_value_dump_destr_str,
            "$!": self._pmlo_stack_dump,
            "$$!": self._pmlo_stack_dump_str,
            # End output functions

            "/$": self._pmlo_number_input,  # Input function TODO(lime) require include
            # TODO(lime) add string input functions

            # Boolean operators TODO(lime) require include
            "||": self._pmlo_boolean_or,
            "&&": self._pmlo_boolean_and,
            "!": self._pmlo_boolean_not,
            # End boolean operators

            # Equality operators TODO(lime) require include
            "==": self._pmlo_equality_eq,
            "!=": self._pmlo_equality_neq,
            ">": self._pmlo_equality_gt,
            "<": self._pmlo_equality_lt,
            ">=": self._pmlo_equality_gt_eq,
            "<=": self._pmlo_equality_lt_eq,
            # End equality operators

            # Bitwise operators TODO(lime) require include
            "~": self._pmlo_bitwise_not,
            "&": self._pmlo_bitwise_and,
            "|": self._pmlo_bitwise_or,
            "^": self._pmlo_bitwise_xor,
            "<<": self._pmlo_bitwise_lshift,
            ">>": self._pmlo_bitwise_rshift,
            # End bitwise operators.
        }

    def _pmlo_find_labels(self):
        for j, token in enumerate(self.all_tokens):
            if token.type == "LABEL":
                if not (token.value in self.labels):
                    self.labels[token.value] = j

    def _pmlo_execute_token(self, token):
        if token.type == "NUMBER":
            self.stacks[self.stack_pointer].append(token.value)

        elif token.type == "FUNCTION":
            try:
                self.builtin_functions[token.value]()
            except KeyError:
                print(f"Function '{token.value}' not defined.")
                exit(1)

        elif token.type == "OPEN_SCOPE":
            self.stacks.append(deque(maxlen=65535))
            self.stack_pointer += 1

        elif token.type == "CLOSE_SCOPE":
            self.stacks[self.stack_pointer - 1].extend(self.stacks[self.stack_pointer])
            self.stacks.pop(self.stack_pointer)
            self.stack_pointer -= 1

        elif token.type == "STRING":
            self.stacks[self.stack_pointer].extend([ord(x) for x in token.value])

        elif token.type == "RANGE":
            start = int(token.value.split("..")[0])
            end = int(token.value.split("..")[1]) + 1
            self.stacks[self.stack_pointer].extend(list(range(start, end)))

        elif token.type == "LABEL_FUNCTION":
            fn = token.value.split(":")[0]
            label = token.value.split(":")[1]
            try:
                label_location = self.labels[label]
            except KeyError as e:
                with pmlo_handle_except(pmlo_handler):
                    raise PMLOLabelNotFoundError(label) from None
            if fn == "jump":
                self.code_pointer = label_location
            elif fn == "jump_if_not_zero":
                val = self.stacks[self.stack_pointer][-1]
                if val != 0:
                    self.code_pointer = label_location
            elif fn == "jump_if_zero":
                val = self.stacks[self.stack_pointer][-1]
                if val == 0:
                    self.code_pointer = label_location
            elif fn == "jump_if_stack_not_empty":
                if len(self.stacks[self.stack_pointer]) != 0:
                    self.code_pointer = label_location
            elif fn == "jump_if_stack_empty":
                if len(self.stacks[self.stack_pointer]) == 0:
                    self.code_pointer = label_location
            elif fn == "jump_if_stack_one":
                if len(self.stacks[self.stack_pointer]) == 1:
                    self.code_pointer = label_location
            elif fn == "jump_if_stack_not_one":
                if len(self.stacks[self.stack_pointer]) != 1:
                    self.code_pointer = label_location

        elif token.type == "REGISTER_FUNCTION":
            fn = token.value.split("(")[0]
            register = token.value.split("(")[1].strip(")")
            if fn == "pop_into":
                self.registers[register] = self.stacks[self.stack_pointer].pop()
            elif fn == "copy_into":
                self.registers[register] = self.stacks[self.stack_pointer][-1]
            elif fn == "pull_from":
                self.stacks[self.stack_pointer].append(self.registers[register])
            elif fn == "print":
                print(self.registers[register])

        elif token.type == "STACK_FUNCTION":
            fn = token.value.split("(")[0]
            stack = int(token.value.split("(")[1].strip(")"))
            if fn == "pop_into":
                self.stacks[stack].append(self.stacks[self.stack_pointer].pop())
            elif fn == "copy_into":
                self.stacks[stack].append(self.stacks[self.stack_pointer][-1])
            elif fn == "pull_from":
                self.stacks[self.stack_pointer].append(self.stacks[stack].pop())
            elif fn == "print":
                print(list(self.stacks[stack])[::-1])

    def execute(self, code):
        self.all_tokens = list(code)
        self._pmlo_find_labels()
        while self.code_pointer != len(self.all_tokens):
            self._pmlo_execute_token(self.all_tokens[self.code_pointer])
            # print(list(self.stacks[self.stack_pointer])[::-1])
            self.code_pointer += 1

    def _pmlo_add(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a + b)

    def _pmlo_subtract(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a - b)

    def _pmlo_multiply(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a * b)

    def _pmlo_power(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a ** b)

    def _pmlo_divide(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a / b)

    def _pmlo_modulo(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a % b)

    def _pmlo_incr(self):
        a = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a + 1)

    def _pmlo_decr(self):
        a = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a - 1)

    def _pmlo_stack_revr(self):
        self.stacks[self.stack_pointer].reverse()

    def _pmlo_stack_dump(self):
        print(list(self.stacks[self.stack_pointer])[::-1])

    def _pmlo_stack_dump_str(self):
        tmp_stk = self.stacks[self.stack_pointer].copy()
        while len(self.stacks[self.stack_pointer]) != 0:
            print(chr(self.stacks[self.stack_pointer].pop()), end="")
        print()
        self.stacks[self.stack_pointer] = tmp_stk

    def _pmlo_value_dump(self):
        print(self.stacks[self.stack_pointer][-1])

    def _pmlo_value_dump_str(self):
        print(chr(self.stacks[self.stack_pointer][-1]))

    def _pmlo_value_dump_destr(self):
        print(self.stacks[self.stack_pointer].pop())

    def _pmlo_value_dump_destr_str(self):
        print(chr(self.stacks[self.stack_pointer].pop()), end="")

    def _pmlo_number_input(self):
        self.stacks[self.stack_pointer].append(int(input(">> ")))

    def _pmlo_boolean_or(self):
        a = bool(self.stacks[self.stack_pointer].pop())
        b = bool(self.stacks[self.stack_pointer].pop())
        self.stacks[self.stack_pointer].append(int(a or b))

    def _pmlo_boolean_and(self):
        a = bool(self.stacks[self.stack_pointer].pop())
        b = bool(self.stacks[self.stack_pointer].pop())
        self.stacks[self.stack_pointer].append(int(a and b))

    def _pmlo_boolean_not(self):
        a = bool(self.stacks[self.stack_pointer].pop())
        self.stacks[self.stack_pointer].append(int(not a))

    def _pmlo_equality_eq(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(int(a == b))
    
    def _pmlo_equality_neq(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(int(a != b))

    def _pmlo_equality_gt(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(int(a > b))
    
    def _pmlo_equality_lt(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(int(a < b))

    def _pmlo_equality_gt_eq(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(int(a >= b))
    
    def _pmlo_equality_lt_eq(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(int(a <= b))
    
    def _pmlo_bitwise_not(self):
        a = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(~a)
    
    def _pmlo_bitwise_and(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a & b)
    
    def _pmlo_bitwise_or(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a | b)

    def _pmlo_bitwise_xor(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a ^ b)

    def _pmlo_bitwise_lshift(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a << b)

    def _pmlo_bitwise_rshift(self):
        a = self.stacks[self.stack_pointer].pop()
        b = self.stacks[self.stack_pointer].pop()
        self.stacks[self.stack_pointer].append(a >> b)
