import os
import tkinter as tk
from tkinter import messagebox
import graphviz

# -----------------------
# Tokenizer (Lexer)
# -----------------------
class Token:
    LET, IDENTIFIER, ASSIGN, NUMBER, PLUS, SEMICOLON, LPAREN, RPAREN, LBRACE, RBRACE, EOF = (
        'LET', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'PLUS', 'SEMICOLON',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'EOF'
    )
    DEF, IF, RETURN, FOR, IN, PRINT, LT, MINUS, COMMA, STRING, EQ = (
        'DEF', 'IF', 'RETURN', 'FOR', 'IN', 'PRINT', 'LT', 'MINUS', 'COMMA', 'STRING', 'EQ'
    )
    MULTIPLY, DIVIDE = 'MULTIPLY', 'DIVIDE'

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

    def peek(self):
        if self.pos + 1 < len(self.text):
            return self.text[self.pos + 1]
        return None

    def get_next_token(self):
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isspace():
                self.advance()
                continue
            if char.isalpha() or char == '_':
                return self._identifier()
            if char.isdigit():
                return self._number()
            if char == '"':
                return self._string()
            if char == '=':
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token(Token.EQ, '==')
                self.advance()
                return Token(Token.ASSIGN, '=')
            if char == '+':
                self.advance()
                return Token(Token.PLUS, '+')
            if char == '-':
                self.advance()
                return Token(Token.MINUS, '-')
            if char == '*':
                self.advance()
                return Token(Token.MULTIPLY, '*')
            if char == '/':
                self.advance()
                return Token(Token.DIVIDE, '/')
            if char == ';':
                self.advance()
                return Token(Token.SEMICOLON, ';')
            if char == ',':
                self.advance()
                return Token(Token.COMMA, ',')
            if char == '<':
                self.advance()
                return Token(Token.LT, '<')
            if char == '(':
                self.advance()
                return Token(Token.LPAREN, '(')
            if char == ')':
                self.advance()
                return Token(Token.RPAREN, ')')
            if char == '{':
                self.advance()
                return Token(Token.LBRACE, '{')
            if char == '}':
                self.advance()
                return Token(Token.RBRACE, '}')

            # Unknown/unsupported char
            self.advance()
        return Token(Token.EOF)

    def _identifier(self):
        result = ''
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            result += self.text[self.pos]
            self.advance()
        keywords = {
            'let': Token.LET,
            'def': Token.DEF,
            'if': Token.IF,
            'return': Token.RETURN,
            'for': Token.FOR,
            'in': Token.IN,
            'print': Token.PRINT,
        }
        token_type = keywords.get(result, Token.IDENTIFIER)
        return Token(token_type, result)

    def _number(self):
        result = ''
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            result += self.text[self.pos]
            self.advance()
        return Token(Token.NUMBER, int(result))

    def _string(self):
        self.advance()  # skip opening quote
        result = ''
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            result += self.text[self.pos]
            self.advance()
        self.advance()  # skip closing quote
        return Token(Token.STRING, result)

# -----------------------
# AST Node and Parser
# -----------------------
class ASTNode:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

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
        program = ASTNode("Program")
        while self.current_token.type != Token.EOF:
            program.add_child(self.statement())
        return program

    def statement(self):
        if self.current_token.type == Token.DEF:
            return self.function_def()
        elif self.current_token.type == Token.IF:
            return self.if_statement()
        elif self.current_token.type == Token.RETURN:
            return self.return_statement()
        elif self.current_token.type == Token.FOR:
            return self.for_statement()
        elif self.current_token.type == Token.PRINT:
            return self.print_statement()
        elif self.current_token.type == Token.IDENTIFIER:
            return self.assignment_or_expression_statement()
        else:
            return self.expression_statement()

    def assignment_or_expression_statement(self):
        saved_pos = self.lexer.pos
        saved_tok = self.current_token
        next_tok = self.lexer.get_next_token()
        self.lexer.pos = saved_pos
        self.current_token = saved_tok

        if next_tok.type == Token.ASSIGN:
            return self.assignment_statement()
        else:
            return self.expression_statement()

    def assignment_statement(self):
        var_name = self.current_token.value
        self.eat(Token.IDENTIFIER)
        self.eat(Token.ASSIGN)
        expr = self.expression()
        if self.current_token.type == Token.SEMICOLON:
            self.eat(Token.SEMICOLON)
        node = ASTNode("Assignment")
        node.add_child(ASTNode("Variable", var_name))
        node.add_child(expr)
        return node

    def expression_statement(self):
        expr = self.expression()
        if self.current_token.type == Token.SEMICOLON:
            self.eat(Token.SEMICOLON)
        return expr

    def function_def(self):
        node = ASTNode("FunctionDef")
        self.eat(Token.DEF)
        func_name = self.current_token.value
        self.eat(Token.IDENTIFIER)
        self.eat(Token.LPAREN)
        params = []
        if self.current_token.type != Token.RPAREN:
            params.append(self.current_token.value)
            self.eat(Token.IDENTIFIER)
            while self.current_token.type == Token.COMMA:
                self.eat(Token.COMMA)
                params.append(self.current_token.value)
                self.eat(Token.IDENTIFIER)
        self.eat(Token.RPAREN)
        self.eat(Token.LBRACE)

        node.value = func_name
        params_node = ASTNode("Parameters")
        for p in params:
            params_node.add_child(ASTNode("Param", p))
        node.add_child(params_node)

        while self.current_token.type != Token.RBRACE:
            node.add_child(self.statement())
        self.eat(Token.RBRACE)
        return node

    def if_statement(self):
        node = ASTNode("IfStatement")
        self.eat(Token.IF)
        self.eat(Token.LPAREN)
        cond = self.expression()
        self.eat(Token.RPAREN)
        self.eat(Token.LBRACE)

        node.add_child(cond)
        body = ASTNode("IfBody")
        while self.current_token.type != Token.RBRACE:
            body.add_child(self.statement())
        self.eat(Token.RBRACE)
        node.add_child(body)
        return node

    def return_statement(self):
        node = ASTNode("ReturnStatement")
        self.eat(Token.RETURN)
        expr = self.expression()
        self.eat(Token.SEMICOLON)
        node.add_child(expr)
        return node

    def for_statement(self):
        node = ASTNode("ForLoop")
        self.eat(Token.FOR)
        self.eat(Token.LPAREN)

        init = self.assignment_statement()
        cond = self.expression()
        self.eat(Token.SEMICOLON)
        incr = self.assignment_statement()

        self.eat(Token.RPAREN)
        self.eat(Token.LBRACE)
        body = ASTNode("ForBody")
        while self.current_token.type != Token.RBRACE:
            body.add_child(self.statement())
        self.eat(Token.RBRACE)

        node.add_child(init)
        node.add_child(cond)
        node.add_child(incr)
        node.add_child(body)
        return node

    def print_statement(self):
        node = ASTNode("PrintStatement")
        self.eat(Token.PRINT)
        self.eat(Token.LPAREN)
        arg = self.expression()
        self.eat(Token.RPAREN)
        self.eat(Token.SEMICOLON)
        node.add_child(arg)
        return node

    def expression(self):
        node = self.term()
        while self.current_token.type in (Token.PLUS, Token.MINUS, Token.LT):
            op = ASTNode("Operator", self.current_token.value)
            if self.current_token.type == Token.PLUS:
                self.eat(Token.PLUS)
            elif self.current_token.type == Token.MINUS:
                self.eat(Token.MINUS)
            elif self.current_token.type == Token.LT:
                self.eat(Token.LT)
            op.add_child(node)
            op.add_child(self.term())
            node = op
        return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (Token.MULTIPLY, Token.DIVIDE):
            op = ASTNode("Operator", self.current_token.value)
            if self.current_token.type == Token.MULTIPLY:
                self.eat(Token.MULTIPLY)
            elif self.current_token.type == Token.DIVIDE:
                self.eat(Token.DIVIDE)
            op.add_child(node)
            op.add_child(self.factor())
            node = op
        return node

    def factor(self):
        tok = self.current_token
        if tok.type == Token.NUMBER:
            self.eat(Token.NUMBER)
            return ASTNode("Number", tok.value)
        elif tok.type == Token.IDENTIFIER:
            id_name = tok.value
            self.eat(Token.IDENTIFIER)
            if self.current_token.type == Token.LPAREN:
                self.eat(Token.LPAREN)
                args = []
                if self.current_token.type != Token.RPAREN:
                    args.append(self.expression())
                    while self.current_token.type == Token.COMMA:
                        self.eat(Token.COMMA)
                        args.append(self.expression())
                self.eat(Token.RPAREN)
                call_node = ASTNode("Call", id_name)
                for arg in args:
                    call_node.add_child(arg)
                return call_node
            return ASTNode("Variable", id_name)
        elif tok.type == Token.STRING:
            self.eat(Token.STRING)
            return ASTNode("String", tok.value)
        elif tok.type == Token.LPAREN:
            self.eat(Token.LPAREN)
            node = self.expression()
            self.eat(Token.RPAREN)
            return node
        else:
            raise SyntaxError(f"Unexpected token {tok.type}")

# -----------------------
# AST Visualization
# -----------------------
class ASTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Recursive Descent Parser – AST Visualizer")

        self.text_input = tk.Text(root, height=20, width=80)
        self.text_input.pack(padx=10, pady=10)

        self.visualize_button = tk.Button(root, text="Visualize AST", command=self.visualize)
        self.visualize_button.pack(pady=(0,10))

    def visualize(self):
        code = self.text_input.get("1.0", tk.END).strip()
        if not code:
            messagebox.showwarning("Input Error", "Please enter code to parse.")
            return
        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            ast = parser.parse()
            self._render_ast(ast)
        except Exception as e:
            messagebox.showerror("Parsing Error", str(e))

    def _render_ast(self, ast):
        dot = graphviz.Digraph(comment='AST')
        self._add_node(dot, ast)
        filename = "ast"
        dot.render(filename, format='png', cleanup=True)
        messagebox.showinfo("AST Generated", f"AST image saved as '{filename}.png'.")

    def _add_node(self, dot, node, parent_id=None, counter=[0]):
        counter[0] += 1
        nid = f"n{counter[0]}"
        label = node.type + (f": {node.value}" if node.value is not None else "")
        dot.node(nid, label)
        if parent_id:
            dot.edge(parent_id, nid)
        for child in node.children:
            self._add_node(dot, child, nid, counter)

# -----------------------
# Main Function
# -----------------------
def main():
    root = tk.Tk()
    app = ASTVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
