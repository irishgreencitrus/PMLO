class PMLOParser:
    def parse_tokens(self,tokens):
        new_tokens = list()
        for tok in tokens:
            t = tok
            if t.type == "STRING":
                t.value = t.value.strip('"')
            elif t.type == "BIN_NUMBER":
                t.type = "NUMBER"
                t.value = float(int(t.value.lstrip("0b"), 2))
            elif t.type == "HEX_NUMBER":
                t.type = "NUMBER"
                t.value = float(int(t.value.lstrip("0x"), 16))
            elif t.type == "INT_NUMBER":
                t.type = "NUMBER"
                t.value = float(t.value)
            elif t.type == "NUMBER":
                t.value = float(t.value)
            elif t.type == "LABEL":
                t.value = t.value.lstrip("::")
            new_tokens.append(t)
        return new_tokens
