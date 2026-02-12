 # -------------------Token--------------------
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"{self.type}({self.value})" if self.value is not None else f"{self.type}"
# -------------------- Lexer--------------------
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = text[self.pos] if text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return Token('NUMBER', int(result))

    def identifier(self):
        result = ''
        while self.current_char and self.current_char.isalnum():
            result += self.current_char
            self.advance()
        if result == 'while':
            return Token('WHILE')
        elif result == 'end':
            return Token('END')
        return Token('IDENT', result)

    def get_next_token(self):
        while self.current_char:
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
            raise Exception(f"Lexer error: {self.current_char}")
        return Token('EOF')

# -------------------- AST Nodes --------------------
class Number:
    def __init__(self, value): self.value = value
class Variable:
    def __init__(self, name): self.name = name
class BinOp:
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
class Assignment:
    def __init__(self, variable, expr): self.variable = variable; self.expr = expr
class PrintStatement:
    def __init__(self, variable): self.variable = variable
class InputStatement:
    def __init__(self, variable): self.variable = variable
class Condition:
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
class WhileStatement:
    def __init__(self, condition, statements): self.condition = condition; self.statements = statements
class Program:
    def __init__(self, statements): self.statements = statements

# -------------------- Parser --------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[self.pos]

    def eat(self, type):
        if self.current_token.type == type:
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else Token('EOF')
        else:
            raise Exception(f"Parser error: expected {type}, got {self.current_token.type}")

    def factor(self):
        tok = self.current_token
        if tok.type == 'NUMBER': self.eat('NUMBER'); return Number(tok.value)
        elif tok.type == 'IDENT': self.eat('IDENT'); return Variable(tok.value)

    def term(self):
        node = self.factor()
        while self.current_token.type in ('MUL','DIV'):
            op = self.current_token.type; self.eat(op)
            node = BinOp(node, op, self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in ('PLUS','MINUS'):
            op = self.current_token.type; self.eat(op)
            node = BinOp(node, op, self.term())
        return node

    def condition(self):
        left = self.expr()
        op = self.current_token.type
        if op not in ('EQ','NE'): raise Exception("Parser error: Only == and != allowed in while")
        self.eat(op)
        right = self.expr()
        return Condition(left, op, right)

    def statement(self):
        tok = self.current_token
        if tok.type == 'EOF' or tok.type == 'END': self.eat(tok.type); return None
        if tok.type == 'IDENT':
            name = tok.value; self.eat('IDENT'); self.eat('ASSIGN')
            expr_node = self.expr()
            return Assignment(Variable(name), expr_node)
        elif tok.type == 'PRINT':
            self.eat('PRINT')
            name = self.current_token.value; self.eat('IDENT')
            return PrintStatement(Variable(name))
        elif tok.type == 'INPUT':
            self.eat('INPUT')
            name = self.current_token.value; self.eat('IDENT')
            return InputStatement(Variable(name))
        elif tok.type == 'WHILE':
            self.eat('WHILE'); cond = self.condition(); stmts=[]
            while self.current_token.type != 'END': s=self.statement(); stmts.append(s)
            self.eat('END')
            return WhileStatement(cond, stmts)
        else:
            raise Exception(f"Parser error: Unexpected {tok.type}")

    def parse(self):
        stmts=[]
        while self.current_token.type != 'EOF':
            s=self.statement()
            if s: stmts.append(s)
        return Program(stmts)

# -------------------- Interpreter --------------------
def eval_expr(node, memory):
    if isinstance(node, Number): return node.value
    elif isinstance(node, Variable):
        if node.name in memory: return memory[node.name]
        raise Exception(f"Runtime error: '{node.name}' not defined")
    elif isinstance(node, BinOp):
        l = eval_expr(node.left, memory); r = eval_expr(node.right, memory)
        return l+r if node.op=='PLUS' else l-r if node.op=='MINUS' else l*r if node.op=='MUL' else l//r

def eval_condition(cond, memory):
    l = eval_expr(cond.left, memory); r = eval_expr(cond.right, memory)
    return (l==r if cond.op=='EQ' else l!=r)

# -------------------- Run program (import-safe) --------------------
def run_program_interactive(code, input_values={}):
    lexer=Lexer(code); tokens=[]
    while True:
        tok=lexer.get_next_token(); tokens.append(tok)
        if tok.type=='EOF': break
    parser=Parser(tokens); ast=parser.parse(); memory={}; output=[]
    def eval_stmt(node):
        if isinstance(node, Assignment): memory[node.variable.name]=eval_expr(node.expr,memory)
        elif isinstance(node, PrintStatement): output.append(str(eval_expr(node.variable,memory)))
        elif isinstance(node, InputStatement):
            var=node.variable.name
            if var in input_values: memory[var]=int(input_values.pop(var))
            else: return {'need_input': var, 'output': output.copy()}
        elif isinstance(node, WhileStatement):
            while eval_condition(node.condition,memory):
                for s in node.statements:
                    res = eval_stmt(s)
                    if res: return res
    for s in ast.statements:
        res = eval_stmt(s)
        if res: return res
    return {'done': True, 'output': output}















