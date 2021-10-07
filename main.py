from pmlo_parser import PMLOParser
from pmlo_transpiler import PMLOGenerateC
from pmlo_lexer import PMLOLexer
from pmlo_executor import PMLOExec

with open("examples/fibonacci_numbers.pmlo") as f:
    global data
    data = f.read()

lexer = PMLOLexer()

lexed_tokens = list(lexer.tokenize(data))
parser = PMLOParser()
lexed_tokens = parser.parse_tokens(lexed_tokens)

executor = PMLOExec()
executor.execute(lexed_tokens)

generator = PMLOGenerateC(lexed_tokens, "test.c")
generator.start_compilation()

