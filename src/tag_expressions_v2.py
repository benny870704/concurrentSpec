import re
import fnmatch

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class TagExpressionsV2:
    def __init__(self):
        self.input = None
        self.tokens = None
        self.parsed_expr = None
        self.token_pos = 0
        self.words_pos = 0

    def lexer(self, input: str):
        self.input = input
        tokens = []
        for match in re.finditer(r"@\w+|\w+|and|or|not|\(|\)", input):
            if match.group() == "and":
                tokens.append(Token("AND", match.group()))
            elif match.group() == "or":
                tokens.append(Token("OR", match.group()))
            elif match.group() == "not":
                tokens.append(Token("NOT", match.group()))
            elif match.group() == "(":
                tokens.append(Token("LPAR", match.group()))
            elif match.group() == ")":
                tokens.append(Token("RPAR", match.group()))
            else:
                tokens.append(Token("TAG", match.group()))
        return tokens

    def consume(self, type):
        token = self.current_token()
        if token.type == type:
            self.token_pos += 1
            if type == "TAG": self.words_pos += 1
        else:
            if type == "RPAR" and token.type == "EOF":
                raise SyntaxError("Missing closing parenthesis.")
            elif type == "TAG" and token.type == "RPAR":
                raise SyntaxError("Missing tag inside parentheses.")
            else:
                raise SyntaxError(f"Unexpected token {token.type} within the given input '{self.input}'.")

    def current_token(self):
        if self.token_pos < len(self.tokens):
            return self.tokens[self.token_pos]
        else:
            return Token("EOF", None)

    def parse(self, expr: str):
        if expr is None: raise ValueError("Invalid input: None.")
        self.tokens = self.lexer(expr)
        self.parsed_expr = self.and_expr()
        # print(self.parsed_expr)
        if self.token_pos != len(self.tokens):
            raise SyntaxError(f"Unexpected token {self.current_token().type} within the given input '{self.input}'.")
        return self.parsed_expr

    def and_expr(self):
        nodes = [self.or_expr()]
        while self.current_token().type == "AND":
            self.consume("AND")
            nodes.append(self.or_expr())
        return ("and", *nodes) if len(nodes) > 1 else nodes[0]

    def or_expr(self):
        nodes = [self.not_expr()]
        while self.current_token().type == "OR":
            self.consume("OR")
            nodes.append(self.not_expr())
        return ("or", *nodes) if len(nodes) > 1 else nodes[0]

    def not_expr(self):
        token = self.current_token()
        if token.type == "NOT":
            self.consume("NOT")
            return ("not", self.not_expr())
        elif token.type == "LPAR":
            self.consume("LPAR")
            node = self.and_expr()
            if self.current_token().type != "RPAR":
                raise SyntaxError(f"Missing closing parenthesis within the given input '{self.input}'.")
            self.consume("RPAR")
            return node
        else:
            self.consume("TAG")
            return token.value[1:] if token.value.startswith("@") else token.value
        
    def match(self, tags: list):
        return self.evaluate(self.parsed_expr, tags) if self.parsed_expr is not None else False

    def evaluate(self, parsed_expr, tags: list):
        # print(f"evaluate {parsed_expr}")
        if parsed_expr[0] == "not":
            # print(f"not {parsed_expr[1]}")
            return not self.evaluate(parsed_expr[1], tags)
        elif parsed_expr[0] == "and":
            # print(f"and {parsed_expr[1]} {parsed_expr[2]}")
            return self.evaluate(parsed_expr[1], tags) and self.evaluate(parsed_expr[2], tags)
        elif parsed_expr[0] == "or":
            # print(f"or {parsed_expr[1]} {parsed_expr[2]}")
            return self.evaluate(parsed_expr[1], tags) or self.evaluate(parsed_expr[2], tags)
        else:
            # print(f"tag {parsed_expr} in {tags}")
            return any(fnmatch.fnmatch(tag, parsed_expr) for tag in tags)