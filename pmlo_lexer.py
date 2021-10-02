from sly import Lexer


class PMLOLexer(Lexer):
    tokens = {
        FUNCTION,
        OPEN_SCOPE,
        CLOSE_SCOPE,
        NUMBER,
        STRING,
        LABEL,
        LABEL_FUNCTION,
        RANGE,
        REGISTER_FUNCTION,
        STACK_FUNCTION,
    }
    ignore = ' \t\n":'
    ignore_comment = r"\@.*"
    STRING = r'(?<=")(?:\\.|[^"\\])*(?=")'
    OPEN_SCOPE = r"\["
    CLOSE_SCOPE = r"\]"
    RANGE = r"\d\.\.\d+"
    NUMBER = r"\d+"
    LABEL = r"(?<=::)[A-Z_]+"
    LABEL_FUNCTION = r"[a-z_]+:[A-Z_]+"
    REGISTER_FUNCTION = r"[a-z_]+<[a-z]>"
    STACK_FUNCTION = r"[a-z_]+<[0-9]+>"

    @_(r"\d+")
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    FUNCTION = r"[a-zA-Z_\+\*!$#=\-%/\|][\w\+\*!$#=\-%/\|]*"
