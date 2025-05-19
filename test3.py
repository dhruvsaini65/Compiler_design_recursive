import os
import tkinter as tk
from tkinter import messagebox
import graphviz

# -----------------------
# Tokenizer (Lexer)
# -----------------------
class Token:
    LET, IDENTIFIER, ASSIGN, NUMBER, PLUS, SEMICOLON, EOF = 'LET', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'PLUS', 'SEMICOLON', 'EOF'

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

# -----------------------
# Parser
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

# -----------------------
# AST Visualization
# -----------------------
class ASTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Recursive Descent Parser - AST Visualizer")

        self.text_input = tk.Text(root, height=3, width=50)
        self.text_input.pack()

        self.visualize_button = tk.Button(root, text="Visualize AST", command=self.generate_ast)
        self.visualize_button.pack()

        self.canvas = tk.Label(root)
        self.canvas.pack()

    def generate_ast(self):
        code = self.text_input.get("1.0", tk.END).strip()

        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            ast = parser.parse()
            self.display_ast(ast)
        except SyntaxError as e:
            messagebox.showerror("Error", str(e))

    def display_ast(self, ast):
        dot = graphviz.Digraph()
        self.build_graph(dot, ast)

        # Ensure output directory exists
        output_dir = "output_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, "ast")
        dot.render(output_path, format='png')

        # Load and display image
        self.canvas.config(text=f"AST saved at {output_path}.png")

    def build_graph(self, dot, node, parent=None):
        node_id = str(id(node))
        dot.node(node_id, f"{node.type}: {node.value}" if node.value else node.type)

        if parent:
            dot.edge(str(id(parent)), node_id)

        for child in node.children:
            self.build_graph(dot, child, node)

# -----------------------
# Main Application
# -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = ASTVisualizer(root)
    root.mainloop()


