from pmlo_transpiler import PMLOGenerateC
from pmlo_lexer import PMLOLexer
from pmlo_executor import PMLOExec

f = open("examples/project_euler_one.pmlo")
data = f.read()
f.close()
lexer = PMLOLexer()
lexed_tokens = list(lexer.tokenize(data))
executor = PMLOExec()
generator = PMLOGenerateC(lexed_tokens, "test.c")
generator.start_compilation()
executor.execute(lexed_tokens)
