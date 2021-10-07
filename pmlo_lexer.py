from sly import Lexer


class PMLOLexer(Lexer):
    tokens = {
        STRING,

        OPEN_SCOPE,
        CLOSE_SCOPE,

        RANGE,
        BIN_NUMBER,
        HEX_NUMBER,
        INT_NUMBER,
        NUMBER,

        LABEL,
        LABEL_FUNCTION,

        REGISTER_FUNCTION,
        STACK_FUNCTION,

        FUNCTION,
    }
    ignore = ' \t\n"'
    ignore_comment = r"\@.*"

    # <== SYNTAX HIGHLIGHT AS A STRING
    STRING = r'".*"'
    # ==>

    # <== SYNTAX HIGHLIGHT THESE THE SAME
    OPEN_SCOPE = r"\["
    CLOSE_SCOPE = r"\]"
    # ==>

    # <== SYNTAX HIGHLIGHT ALL OF THESE AS NUMBERS
    RANGE = r"\d\.\.\d+"
    BIN_NUMBER = r"0b[0-1]+"
    HEX_NUMBER = r"0x[0-9A-Fa-f]+"
    NUMBER = r"-?\d+\.\d+"
    INT_NUMBER = r"-?\d+"
    # ==>

    # <== SYNTAX HIGHLIGHT THESE THE SAME
    LABEL = r"::[A-Z_]+"
    LABEL_FUNCTION = r"[a-z_]+:[A-Z_]+"
    # ==>

    # <== SYNTAX HIGHLIGHT THESE DIFFERENTLY
    REGISTER_FUNCTION = r"[a-z_]+\([a-z]\)"
    STACK_FUNCTION = r"[a-z_]+\([0-9]+\)"
    # ==>

    FUNCTION = r"[a-zA-Z_\+\*!$#=\-%/\|<>~^][\w\+\*!$#=\-%/\|<>~^]*"
