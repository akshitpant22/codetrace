import ast
import math
from collections import Counter
from dataclasses import dataclass, field

import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

_TS_LANGUAGES = {
    "c":    Language(tsc.language()),
    "cpp":  Language(tscpp.language()),
    "java": Language(tsjava.language()),
}

SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java"}

_PYTHON_BINOP_LABELS = {
    ast.Add:    "OP_ADD",   ast.Sub:    "OP_SUB",
    ast.Mult:   "OP_MUL",   ast.Div:    "OP_DIV",
    ast.Mod:    "OP_MOD",   ast.Pow:    "OP_POW",
    ast.FloorDiv: "OP_FLOORDIV",
    ast.BitAnd: "OP_BITAND", ast.BitOr: "OP_BITOR",
    ast.BitXor: "OP_BITXOR", ast.LShift: "OP_LSHIFT",
    ast.RShift: "OP_RSHIFT",
}

_PYTHON_CMPOP_LABELS = {
    ast.Eq:    "CMP_EQ",  ast.NotEq: "CMP_NEQ",
    ast.Lt:    "CMP_LT",  ast.LtE:   "CMP_LTE",
    ast.Gt:    "CMP_GT",  ast.GtE:   "CMP_GTE",
    ast.Is:    "CMP_IS",  ast.IsNot: "CMP_ISNOT",
    ast.In:    "CMP_IN",  ast.NotIn: "CMP_NOTIN",
}

_PYTHON_BOOLOP_LABELS = {
    ast.And: "BOOL_AND",
    ast.Or:  "BOOL_OR",
}

_PYTHON_UNARYOP_LABELS = {
    ast.Not:    "UNARY_NOT",
    ast.UAdd:   "UNARY_PLUS",
    ast.USub:   "UNARY_MINUS",
    ast.Invert: "UNARY_INVERT",
}

_PYTHON_AUGOP_LABELS = {
    ast.Add:  "AUG_ADD", ast.Sub:  "AUG_SUB",
    ast.Mult: "AUG_MUL", ast.Div:  "AUG_DIV",
    ast.Mod:  "AUG_MOD",
}

_TS_OPERATOR_LABELS = {
    "+": "OP_ADD",  "-":  "OP_SUB",  "*":  "OP_MUL",
    "/": "OP_DIV",  "%":  "OP_MOD",  "**": "OP_POW",
    "&": "OP_BITAND", "|": "OP_BITOR", "^": "OP_BITXOR",
    "<<": "OP_LSHIFT", ">>": "OP_RSHIFT",
    "==": "CMP_EQ",  "!=": "CMP_NEQ",
    "<":  "CMP_LT",  "<=": "CMP_LTE",
    ">":  "CMP_GT",  ">=": "CMP_GTE",
    "&&": "BOOL_AND", "||": "BOOL_OR",
    "+=": "AUG_ADD",  "-=": "AUG_SUB",
    "*=": "AUG_MUL",  "/=": "AUG_DIV",
}


@dataclass
class SemanticFeatures:
    operators:    Counter = field(default_factory=Counter)
    control_flow: Counter = field(default_factory=Counter)
    calls:        Counter = field(default_factory=Counter)
    literals:     Counter = field(default_factory=Counter)
    assignments:  int = 0
    returns:      int = 0

    def to_vector(self) -> dict[str, float]:
        vec: dict[str, float] = {}
        for key, count in self.operators.items():
            vec[f"op_{key}"] = count
        for key, count in self.control_flow.items():
            vec[f"cf_{key}"] = count
        for key, count in self.calls.items():
            vec[f"call_{key}"] = count
        for key, count in self.literals.items():
            vec[f"lit_{key}"] = count
        vec["assignments"] = self.assignments
        vec["returns"]     = self.returns
        return vec


def _cosine_similarity(vec1: dict, vec2: dict) -> float:
    keys = set(vec1) | set(vec2)
    if not keys:
        return 1.0

    dot   = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in keys)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

    if norm1 == 0 and norm2 == 0:
        return 1.0
    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)


def _extract_python_features(source: str) -> SemanticFeatures:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Python SyntaxError: {e}")

    feat = SemanticFeatures()

    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp):
            label = _PYTHON_BINOP_LABELS.get(type(node.op), "OP_OTHER")
            feat.operators[label] += 1

        elif isinstance(node, ast.Compare):
            for op in node.ops:
                label = _PYTHON_CMPOP_LABELS.get(type(op), "CMP_OTHER")
                feat.operators[label] += 1

        elif isinstance(node, ast.BoolOp):
            label = _PYTHON_BOOLOP_LABELS.get(type(node.op), "BOOL_OTHER")
            feat.operators[label] += 1

        elif isinstance(node, ast.UnaryOp):
            label = _PYTHON_UNARYOP_LABELS.get(type(node.op), "UNARY_OTHER")
            feat.operators[label] += 1

        elif isinstance(node, ast.AugAssign):
            label = _PYTHON_AUGOP_LABELS.get(type(node.op), "AUG_OTHER")
            feat.operators[label] += 1
            feat.assignments += 1

        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
            feat.assignments += 1

        elif isinstance(node, ast.Return):
            feat.returns += 1

        elif isinstance(node, (ast.If,)):
            feat.control_flow["IF"] += 1
            if node.orelse:
                feat.control_flow["ELSE"] += 1

        elif isinstance(node, ast.For):
            feat.control_flow["FOR"] += 1

        elif isinstance(node, ast.While):
            feat.control_flow["WHILE"] += 1

        elif isinstance(node, ast.Break):
            feat.control_flow["BREAK"] += 1

        elif isinstance(node, ast.Continue):
            feat.control_flow["CONTINUE"] += 1

        elif isinstance(node, ast.Try):
            feat.control_flow["TRY"] += 1

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                feat.calls[node.func.id] += 1
            elif isinstance(node.func, ast.Attribute):
                feat.calls[node.func.attr] += 1
            else:
                feat.calls["CALL"] += 1

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                feat.literals["BOOL"] += 1
            elif isinstance(node.value, int):
                feat.literals["INT"] += 1
            elif isinstance(node.value, float):
                feat.literals["FLOAT"] += 1
            elif isinstance(node.value, str):
                feat.literals["STRING"] += 1

    return feat


def _extract_treesitter_features(source: str, language: str) -> SemanticFeatures:
    try:
        parser = Parser(language=_TS_LANGUAGES[language])
        tree = parser.parse(bytes(source, "utf-8"))
    except Exception as e:
        raise ValueError(f"Tree-sitter failed to parse {language} source: {e}")

    feat = SemanticFeatures()

    def _walk(node) -> None:
        ntype = node.type
        text = node.text.decode("utf-8").strip() if node.text else ""

        if ntype == "binary_expression":
            for child in node.children:
                if not child.is_named and child.text:
                    op = child.text.decode("utf-8").strip()
                    label = _TS_OPERATOR_LABELS.get(op, "OP_OTHER")
                    feat.operators[label] += 1

        elif ntype == "compound_assignment_operator":
            op = text
            label = _TS_OPERATOR_LABELS.get(op, "AUG_OTHER")
            feat.operators[label] += 1
            feat.assignments += 1

        elif ntype == "unary_expression":
            for child in node.children:
                if not child.is_named and child.text:
                    op = child.text.decode("utf-8").strip()
                    if op == "!":
                        feat.operators["UNARY_NOT"] += 1
                    elif op == "-":
                        feat.operators["UNARY_MINUS"] += 1

        elif ntype in {"assignment_expression", "variable_declarator",
                       "local_variable_declaration", "declaration"}:
            feat.assignments += 1

        elif ntype == "return_statement":
            feat.returns += 1

        elif ntype == "if_statement":
            feat.control_flow["IF"] += 1
        elif ntype in {"else_clause", "else"}:
            feat.control_flow["ELSE"] += 1
        elif ntype in {"for_statement", "enhanced_for_statement"}:
            feat.control_flow["FOR"] += 1
        elif ntype == "while_statement":
            feat.control_flow["WHILE"] += 1
        elif ntype == "do_statement":
            feat.control_flow["DO_WHILE"] += 1
        elif ntype in {"switch_statement", "switch_expression"}:
            feat.control_flow["SWITCH"] += 1
        elif ntype == "break_statement":
            feat.control_flow["BREAK"] += 1
        elif ntype == "continue_statement":
            feat.control_flow["CONTINUE"] += 1
        elif ntype == "try_statement":
            feat.control_flow["TRY"] += 1

        elif ntype in {"call_expression", "method_invocation"}:
            feat.calls["CALL"] += 1

        elif ntype in {"number_literal", "integer_literal",
                       "decimal_integer_literal", "hex_integer_literal"}:
            feat.literals["INT"] += 1
        elif ntype in {"floating_point_literal", "decimal_floating_point_literal"}:
            feat.literals["FLOAT"] += 1
        elif ntype in {"string_literal", "string_content"}:
            feat.literals["STRING"] += 1
        elif ntype in {"true", "false"}:
            feat.literals["BOOL"] += 1

        for child in node.children:
            _walk(child)

    _walk(tree.root_node)
    return feat


def extract_semantic_features(source: str, language: str) -> SemanticFeatures:
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )
    if lang == "python":
        return _extract_python_features(source)
    return _extract_treesitter_features(source, lang)


def compare_semantic(source1: str, source2: str, language: str) -> float:
    feat1 = extract_semantic_features(source1, language)
    feat2 = extract_semantic_features(source2, language)

    vec1 = feat1.to_vector()
    vec2 = feat2.to_vector()

    similarity = _cosine_similarity(vec1, vec2)
    return round(similarity * 100, 2)
