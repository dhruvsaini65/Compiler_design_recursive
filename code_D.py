class Token:
    LET, IDENTIFIER, ASSIGN, NUMBER, PLUS, SEMICOLON, EOF = (
        'LET', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'PLUS', 'SEMICOLON', 'EOF'
    )

    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def advance(self):
        self.pos += 1

    def get_next_token(self):
        while self.pos < len(self.text):
            char = self.text[self.pos]

            if char.isspace():
                self.advance()
                continue
            if char.isalpha():
                return self._identifier()
            if char.isdigit():
                return self._number()
            if char == '=':
                self.advance()
                return Token(Token.ASSIGN, '=')
            if char == '+':
                self.advance()
                return Token(Token.PLUS, '+')
            if char == ';':
                self.advance()
                return Token(Token.SEMICOLON, ';')

            self.advance()

        return Token(Token.EOF)

    def _identifier(self):
        result = ''
        while self.pos < len(self.text) and self.text[self.pos].isalnum():
            result += self.text[self.pos]
            self.advance()

        if result == "let":
            return Token(Token.LET, result)
        return Token(Token.IDENTIFIER, result)

    def _number(self):
        result = ''
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            result += self.text[self.pos]
            self.advance()
        return Token(Token.NUMBER, int(result))
