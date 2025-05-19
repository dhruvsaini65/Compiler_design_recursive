class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token.type}")

    def parse(self):
        return self.statement()

    def statement(self):
        self.eat(Token.LET)
        var_node = ASTNode("Variable", self.current_token.value)
        self.eat(Token.IDENTIFIER)

        self.eat(Token.ASSIGN)
        expr_node = self.expression()
        self.eat(Token.SEMICOLON)

        assign_node = ASTNode("Assignment")
        assign_node.add_child(var_node)
        assign_node.add_child(expr_node)
        return assign_node

    # Note: expression() and term() are work-in-progress for full arithmetic support
    def expression(self):
        node = self.term()
        while self.current_token.type == Token.PLUS:
            op_node = ASTNode("Operator", self.current_token.value)
            self.eat(Token.PLUS)
            op_node.add_child(node)
            op_node.add_child(self.term())
            node = op_node
        return node

    def term(self):
        token = self.current_token
        if token.type == Token.NUMBER:
            self.eat(Token.NUMBER)
            return ASTNode("Number", token.value)
        elif token.type == Token.IDENTIFIER:
            self.eat(Token.IDENTIFIER)
            return ASTNode("Variable", token.value)
