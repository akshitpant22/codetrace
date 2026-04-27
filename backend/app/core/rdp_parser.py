import difflib
import json
import re
from enum import Enum, auto
from typing import List, Dict, Any, Optional

class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

KEYWORDS = {
    'def', 'if', 'else', 'elif', 'for', 'while', 'return',
    'import', 'class', 'pass', 'break', 'continue',
    'and', 'or', 'not', 'in', 'is', 'True', 'False', 'None'
}

class Token:
    def __init__(self, type_: TokenType, value: str, line: int):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line})"

class Tokenizer:
    """
    Lexical Analyzer that converts Python source code into a list of Tokens.
    It tracks indentation using a stack to emit INDENT and DEDENT tokens,
    which is critical for Python's whitespace-significant syntax.
    """
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.line_num = 1
        self.indent_stack = [0]
        self.token_specification = [
            ('STRING',     r'(".*?"|\'.*?\')'),
            ('NUMBER',     r'\d+\.\d+|\d+'),
            ('IDENT',      r'[A-Za-z_]\w*'),
            ('OPERATOR',   r'==|!=|<=|>=|//|\*\*|\+=|-=|\+|-|\*|/|%|<|>|='),
            ('PUNCTUATION',r'[:,\(\)\[\]\{\}]'),
            ('WHITESPACE', r'[ \t]+'),
            ('MISMATCH',   r'.'),
        ]
        self.tok_regex = re.compile('|'.join('(?P<%s>%s)' % pair for pair in self.token_specification))

    def tokenize(self) -> List[Token]:
        lines = self.source_code.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            if '#' in line:
                line = line.split('#')[0]
            if not line.strip():
                continue
            indent_level = len(line) - len(line.lstrip())
            
            if indent_level > self.indent_stack[-1]:
                self.indent_stack.append(indent_level)
                self.tokens.append(Token(TokenType.INDENT, "", line_num))
            elif indent_level < self.indent_stack[-1]:
                while indent_level < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append(Token(TokenType.DEDENT, "", line_num))
                if indent_level != self.indent_stack[-1]:
                    raise IndentationError(f"Unindent does not match any outer indentation level at line {line_num}")
            for mo in self.tok_regex.finditer(line.strip()):
                kind = mo.lastgroup
                value = mo.group()
                
                if kind == 'WHITESPACE':
                    continue
                elif kind == 'IDENT':
                    type_ = TokenType.KEYWORD if value in KEYWORDS else TokenType.IDENTIFIER
                    self.tokens.append(Token(type_, value, line_num))
                elif kind == 'NUMBER':
                    self.tokens.append(Token(TokenType.NUMBER, value, line_num))
                elif kind == 'STRING':
                    self.tokens.append(Token(TokenType.STRING, value, line_num))
                elif kind == 'OPERATOR':
                    self.tokens.append(Token(TokenType.OPERATOR, value, line_num))
                elif kind == 'PUNCTUATION':
                    self.tokens.append(Token(TokenType.PUNCTUATION, value, line_num))
                elif kind == 'MISMATCH':
                    raise SyntaxError(f"Unexpected character {value!r} at line {line_num}")
            self.tokens.append(Token(TokenType.NEWLINE, "\n", line_num))
            self.line_num = line_num
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, "", self.line_num))
            
        self.tokens.append(Token(TokenType.EOF, "", self.line_num))
        return self.tokens

class Parser:
    """
    A Top-Down Recursive Descent Parser.
    It builds a syntax tree by recursively matching structural rules (e.g. if statement, loops).
    This technique relies on "lookahead" (peek) to decide which production rule to apply.
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        """Returns the next token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def consume(self, expected_type: Optional[TokenType] = None, expected_value: Optional[str] = None) -> Token:
        """Consumes and returns the next token. Raises an error if expectations fail."""
        token = self.peek()
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type.name}, got {token.type.name} at line {token.line}")
        if expected_value and token.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{token.value}' at line {token.line}")
        self.pos += 1
        return token

    def check(self, expected_type: TokenType, expected_value: Optional[str] = None) -> bool:
        """Safely checks if the next token matches a specific type and value."""
        token = self.peek()
        if token.type != expected_type:
            return False
        if expected_value and token.value != expected_value:
            return False
        return True

    def match(self, expected_type: TokenType, expected_value: Optional[str] = None) -> bool:
        """Consumes the token if it matches, returning True. Otherwise False."""
        if self.check(expected_type, expected_value):
            self.consume()
            return True
        return False

    def skip_newlines(self):
        """Ignores empty newlines which don't affect AST structure."""
        while self.check(TokenType.NEWLINE):
            self.consume()

    def parse(self) -> Dict[str, Any]:
        """Entry point for parsing a program. A program is a list of statements."""
        body = []
        self.skip_newlines()
        while not self.check(TokenType.EOF):
            body.append(self.parse_statement())
            self.skip_newlines()
            
        return {
            "type": "Program",
            "body": body
        }

    def parse_statement(self) -> Dict[str, Any]:
        """Routes to the correct parsing function based on the next keyword/token."""
        token = self.peek()
        if token.type == TokenType.KEYWORD:
            if token.value == 'def':
                return self.parse_function_def()
            elif token.value == 'class':
                return self.parse_class_def()
            elif token.value == 'if':
                return self.parse_if_statement()
            elif token.value == 'for':
                return self.parse_for_loop()
            elif token.value == 'while':
                return self.parse_while_loop()
            elif token.value == 'return':
                return self.parse_return()
            elif token.value == 'import':
                return self.parse_import()
            elif token.value == 'pass':
                return self.parse_pass()
        return self.parse_assign_or_expr()

    def parse_block(self) -> List[Dict[str, Any]]:
        """Parses an indented block of statements. Crucial for Python's scope."""
        self.consume(TokenType.NEWLINE)
        self.consume(TokenType.INDENT)
        body = []
        while not self.check(TokenType.DEDENT) and not self.check(TokenType.EOF):
            if self.check(TokenType.NEWLINE):
                self.consume()
                continue
            body.append(self.parse_statement())
        self.consume(TokenType.DEDENT)
        return body

    def read_until(self, stop_values: List[str]) -> str:
        """Helper to read raw expressions (like conditions) until a specific token."""
        tokens_val = []
        while self.peek().value not in stop_values and self.peek().type not in (TokenType.NEWLINE, TokenType.EOF):
            tokens_val.append(self.consume().value)
        return " ".join(tokens_val)

    def parse_function_def(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'def')
        name = self.consume(TokenType.IDENTIFIER).value
        self.consume(TokenType.PUNCTUATION, '(')
        
        params = []
        while not self.check(TokenType.PUNCTUATION, ')'):
            if self.check(TokenType.IDENTIFIER):
                params.append(self.consume().value)
            else:
                self.consume()
                
        self.consume(TokenType.PUNCTUATION, ')')
        self.consume(TokenType.PUNCTUATION, ':')
        body = self.parse_block()
        
        return {
            "type": "FunctionDef",
            "name": name,
            "params": params,
            "body": body
        }

    def parse_class_def(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'class')
        name = self.consume(TokenType.IDENTIFIER).value
        if self.match(TokenType.PUNCTUATION, '('):
            self.read_until([')'])
            self.consume(TokenType.PUNCTUATION, ')')
            
        self.consume(TokenType.PUNCTUATION, ':')
        body = self.parse_block()
        
        return {
            "type": "ClassDef",
            "name": name,
            "body": body
        }

    def parse_if_statement(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'if')
        condition = self.read_until([':'])
        self.consume(TokenType.PUNCTUATION, ':')
        body = self.parse_block()
        
        else_body = []
        self.skip_newlines()
        
        if self.match(TokenType.KEYWORD, 'elif'):
            self.pos -= 1 
            self.tokens[self.pos].value = 'if'
            else_body.append(self.parse_if_statement())
            
        elif self.match(TokenType.KEYWORD, 'else'):
            self.consume(TokenType.PUNCTUATION, ':')
            else_body = self.parse_block()

        return {
            "type": "IfStatement",
            "condition": condition,
            "body": body,
            "else_body": else_body
        }

    def parse_for_loop(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'for')
        var = self.read_until(['in']).strip()
        self.consume(TokenType.KEYWORD, 'in')
        iterable = self.read_until([':'])
        self.consume(TokenType.PUNCTUATION, ':')
        body = self.parse_block()
        
        return {
            "type": "ForLoop",
            "var": var,
            "iterable": iterable,
            "body": body
        }

    def parse_while_loop(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'while')
        condition = self.read_until([':'])
        self.consume(TokenType.PUNCTUATION, ':')
        body = self.parse_block()
        
        return {
            "type": "WhileLoop",
            "condition": condition,
            "body": body
        }

    def parse_return(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'return')
        expr = self.read_until([])
        self.consume(TokenType.NEWLINE)
        
        return {
            "type": "ReturnStatement",
            "expr": expr
        }
        
    def parse_import(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'import')
        module = self.read_until([])
        self.consume(TokenType.NEWLINE)
        return {
            "type": "ImportStatement",
            "module": module
        }

    def parse_pass(self) -> Dict[str, Any]:
        self.consume(TokenType.KEYWORD, 'pass')
        self.consume(TokenType.NEWLINE)
        return {
            "type": "PassStatement"
        }

    def parse_assign_or_expr(self) -> Dict[str, Any]:
        """Parses variable assignments (x = 5) or plain expressions (foo())."""
        raw_expr = self.read_until([])
        self.consume(TokenType.NEWLINE)
        
        if '=' in raw_expr and '==' not in raw_expr:
            parts = raw_expr.split('=', 1)
            return {
                "type": "AssignStatement",
                "var": parts[0].strip(),
                "expr": parts[1].strip()
            }
            
        return {
            "type": "ExprStatement",
            "expr": raw_expr
        }

def get_node_sequence(tree: Dict[str, Any]) -> List[str]:
    """
    Flattens the parse tree into a sequence of node type strings.
    This sequence is used to detect structural plagiarism (e.g. loops and conditionals matching).
    """
    sequence = []
    
    if not isinstance(tree, dict) or "type" not in tree:
        return sequence
        
    node_type = tree["type"]
    sequence.append(node_type)
    if "body" in tree and isinstance(tree["body"], list):
        for child in tree["body"]:
            sequence.extend(get_node_sequence(child))
            
    if "else_body" in tree and isinstance(tree["else_body"], list):
        for child in tree["else_body"]:
            sequence.extend(get_node_sequence(child))
            
    return sequence

def get_parse_tree(code: str) -> Dict[str, Any]:
    """Tokenizes and parses code, returning the full AST dict."""
    try:
        tokenizer = Tokenizer(code)
        tokens = tokenizer.tokenize()
        parser = Parser(tokens)
        return parser.parse()
    except Exception as e:
        return {"error": str(e), "type": "Error"}

def compare_trees(code1: str, code2: str) -> float:
    """
    Compares two code snippets by generating their ASTs, flattening them,
    and running a sequence matching algorithm. Returns a similarity score 0.0 to 1.0.
    """
    tree1 = get_parse_tree(code1)
    tree2 = get_parse_tree(code2)
    
    seq1 = get_node_sequence(tree1)
    seq2 = get_node_sequence(tree2)
    
    if not seq1 or not seq2:
        return 0.0
        
    matcher = difflib.SequenceMatcher(None, seq1, seq2)
    return matcher.ratio()

if __name__ == "__main__":
    print("="*50)
    print("CODE TRACE - RDP PARSER TEST")
    print("="*50)
    code_func = '''
def greet(name):
    print("Hello", name)
    return True
'''
    print("\n1. Parsing Simple Function:")
    tree1 = get_parse_tree(code_func)
    print(json.dumps(tree1, indent=2))
    code_complex = '''
def find_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            return n
        else:
            pass
'''
    print("\n2. Parsing Nested Loops and Conditionals:")
    tree2 = get_parse_tree(code_complex)
    print(json.dumps(tree2, indent=2))
    code_plagiarized = '''
def get_evens(nums):
    for item in nums:
        if item % 2 == 0:
            return item
        else:
            pass
'''
    print("\n3. Testing Plagiarism Detection (Structural Similarity):")
    score = compare_trees(code_complex, code_plagiarized)
    
    print(f"Original sequence: {get_node_sequence(get_parse_tree(code_complex))}")
    print(f"Suspect sequence:  {get_node_sequence(get_parse_tree(code_plagiarized))}")
    print(f"Similarity Score:  {score * 100:.2f}%")
