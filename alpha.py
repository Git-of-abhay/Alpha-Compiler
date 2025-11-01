import sys

class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    def __repr__(self):
        if self.value is not None:
            return f"{self.type}({self.value})"
        return f"{self.type}"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[self.pos] if text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token('NUMBER', int(result))

    def identifier(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        if result == 'while':
            return Token('WHILE')
        elif result == 'end':
            return Token('END')
        return Token('IDENT', result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                return self.identifier()
            if self.current_char.isdigit():
                return self.number()
            if self.current_char == '+':
                self.advance()
                return Token('PLUS')
            if self.current_char == '-':
                self.advance()
                return Token('MINUS')
            if self.current_char == '*':
                self.advance()
                return Token('MUL')
            if self.current_char == '/':
                self.advance()
                return Token('DIV')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('EQ')
                return Token('ASSIGN')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token('NE')
            if self.current_char == '<':
                self.advance()
                return Token('PRINT')
            if self.current_char == '>':
                self.advance()
                return Token('INPUT')
            if self.current_char == ';':
                self.advance()
                return Token('EOF')
            raise Exception(f"Lexer error: Unexpected character {self.current_char}")
        return Token('EOF')

class Number:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Number({self.value})"

class Variable:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Variable({self.name})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Assignment:
    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr

class PrintStatement:
    def __init__(self, variable):
        self.variable = variable

class InputStatement:
    def __init__(self, variable):
        self.variable = variable

class Condition:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class WhileStatement:
    def __init__(self, condition, statements):
        self.condition = condition
        self.statements = statements

class Program:
    def __init__(self, statements):
        self.statements = statements

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[self.pos]

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF')
        else:
            raise Exception(f"Parser error: expected {token_type}, got {self.current_token.type}")

    def factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return Number(token.value)
        elif token.type == 'IDENT':
            self.eat('IDENT')
            return Variable(token.value)

    def term(self):
        node = self.factor()
        while self.current_token.type in ('MUL', 'DIV'):
            op = self.current_token.type
            self.eat(op)
            node = BinOp(node, op, self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.eat(op)
            node = BinOp(node, op, self.term())
        return node

    def condition(self):
        left = self.expr()
        op = self.current_token.type
        if op not in ('EQ','NE'):
            raise Exception(f"Parser error: Only == and != allowed in while, got {op}")
        self.eat(op)
        right = self.expr()
        return Condition(left, op, right)

    def statement(self):
        token = self.current_token
        if token.type == 'EOF':
            return None
        if token.type == 'END':
            self.eat('END')
            return None
        if token.type == 'IDENT':
            var_name = token.value
            self.eat('IDENT')
            self.eat('ASSIGN')
            expr_node = self.expr()
            return Assignment(Variable(var_name), expr_node)
        elif token.type == 'PRINT':
            self.eat('PRINT')
            var_name = self.current_token.value
            self.eat('IDENT')
            return PrintStatement(Variable(var_name))
        elif token.type == 'INPUT':
            self.eat('INPUT')
            var_name = self.current_token.value
            self.eat('IDENT')
            return InputStatement(Variable(var_name))
        elif token.type == 'WHILE':
            self.eat('WHILE')
            cond = self.condition()
            stmts = []
            while self.current_token.type != 'END':
                stmts.append(self.statement())
            self.eat('END')
            return WhileStatement(cond, stmts)
        else:
            raise Exception(f"Parser error: Unexpected token {token.type}")

    def parse(self):
        statements = []
        while self.current_token.type != 'EOF':
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return Program(statements)

def eval_expr(node, memory):
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, Variable):
        if node.name in memory:
            return memory[node.name]
        else:
            raise Exception(f"Runtime error: Variable '{node.name}' not defined")
    elif isinstance(node, BinOp):
        left = eval_expr(node.left, memory)
        right = eval_expr(node.right, memory)
        if node.op == 'PLUS': return left + right
        if node.op == 'MINUS': return left - right
        if node.op == 'MUL': return left * right
        if node.op == 'DIV': return left // right

def eval_condition(cond, memory):
    left = eval_expr(cond.left, memory)
    right = eval_expr(cond.right, memory)
    if cond.op == 'EQ': return left == right
    if cond.op == 'NE': return left != right


def run_program_interactive(code, input_values={}):
    lexer = Lexer(code)
    tokens = []
    while True:
        tok = lexer.get_next_token()
        tokens.append(tok)
        if tok.type == 'EOF':
            break
    parser = Parser(tokens)
    ast = parser.parse()
    memory = {}
    output = []

    
    def eval_stmt_web(node):
        if isinstance(node, Assignment):
            memory[node.variable.name] = eval_expr(node.expr, memory)
        elif isinstance(node, PrintStatement):
            output.append(str(eval_expr(node.variable, memory)))
        elif isinstance(node, InputStatement):
            var = node.variable.name
            if var in input_values:
                memory[var] = int(input_values.pop(var))
            else:
               
                return {'need_input': var, 'output': output.copy()}
        elif isinstance(node, WhileStatement):
            while eval_condition(node.condition, memory):
                for stmt in node.statements:
                    res = eval_stmt_web(stmt)
                    if res is not None:
                        return res

    for stmt in ast.statements:
        res = eval_stmt_web(stmt)
        if res is not None:
            return res
    return {'done': True, 'output': output}
