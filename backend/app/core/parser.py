import ast
import difflib
from dataclasses import dataclass, field

import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

_TS_LANGUAGES = {
    "c":    Language(tsc.language(), 'c'),
    "cpp":  Language(tscpp.language(), 'cpp'),
    "java": Language(tsjava.language(), 'java'),
}

_PYTHON_STRUCTURAL_NODES = {
    ast.FunctionDef:      "FUNC_DEF",
    ast.AsyncFunctionDef: "FUNC_DEF",
    ast.ClassDef:         "CLASS_DEF",
    ast.For:              "LOOP_FOR",
    ast.AsyncFor:         "LOOP_FOR",
    ast.While:            "LOOP_WHILE",
    ast.If:               "COND_IF",
    ast.Try:              "TRY",
    ast.With:             "WITH",
    ast.Return:           "RETURN",
}

_TS_STRUCTURAL_NODES = {
    "function_definition":     "FUNC_DEF",
    "for_statement":           "LOOP_FOR",
    "while_statement":         "LOOP_WHILE",
    "do_statement":            "LOOP_DO",
    "if_statement":            "COND_IF",
    "switch_statement":        "COND_SWITCH",
    "return_statement":        "RETURN",
    "try_statement":           "TRY",
    "method_declaration":      "FUNC_DEF",
    "constructor_declaration": "FUNC_DEF",
    "enhanced_for_statement":  "LOOP_FOR",
    "switch_expression":       "COND_SWITCH",
    "class_declaration":       "CLASS_DEF",
}

SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java"}

@dataclass
class ASTFeatures:
    fingerprint: list[str] = field(default_factory=list)
    func_count:  int = 0
    loop_count:  int = 0
    cond_count:  int = 0
    max_depth:   int = 0

def _extract_python_features(source: str) -> ASTFeatures:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Python SyntaxError: {e}")

    features = ASTFeatures()

    def _walk(node: ast.AST, depth: int = 0) -> None:
        features.max_depth = max(features.max_depth, depth)
        label = _PYTHON_STRUCTURAL_NODES.get(type(node))
        if label:
            features.fingerprint.append(label)
            if label == "FUNC_DEF":
                features.func_count += 1
            elif label.startswith("LOOP_"):
                features.loop_count += 1
            elif label.startswith("COND_"):
                features.cond_count += 1
        for child in ast.iter_child_nodes(node):
            _walk(child, depth + 1)

    _walk(tree)
    return features

def _extract_treesitter_features(source: str, language: str) -> ASTFeatures:
    try:
        parser = Parser(language=_TS_LANGUAGES[language])
        tree = parser.parse(bytes(source, "utf-8"))
    except Exception as e:
        raise ValueError(f"Tree-sitter failed to parse {language} source: {e}")

    features = ASTFeatures()

    def _walk(node, depth: int = 0) -> None:
        features.max_depth = max(features.max_depth, depth)
        if node.is_named:
            label = _TS_STRUCTURAL_NODES.get(node.type)
            if label:
                features.fingerprint.append(label)
                if label == "FUNC_DEF":
                    features.func_count += 1
                elif label.startswith("LOOP_"):
                    features.loop_count += 1
                elif label.startswith("COND_"):
                    features.cond_count += 1
        for child in node.children:
            _walk(child, depth + 1)

    _walk(tree.root_node)
    return features

def extract_features(source: str, language: str) -> ASTFeatures:
    lang = language.lower().strip()

    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    if lang == "python":
        return _extract_python_features(source)
    else:
        return _extract_treesitter_features(source, lang)

def normalize_loops(fingerprint: list[str]) -> list[str]:
    """
    Normalizes different loop types (for, while, do-while) into a generic
    LOOP_STRUCTURE. This helps detect when the same logic is implemented
    using a different type of loop.
    """
    return ["LOOP_STRUCTURE" if label.startswith("LOOP_") else label for label in fingerprint]

def normalize_conditions(fingerprint: list[str]) -> list[str]:
    """
    Normalizes different conditional types (if, switch) into a generic
    CONDITION_STRUCTURE. This helps detect when the same branching logic
    is implemented using different conditional statements.
    """
    return ["CONDITION_STRUCTURE" if label.startswith("COND_") else label for label in fingerprint]

def compare_syntax(source1: str, source2: str, language: str) -> float:
    features1 = extract_features(source1, language)
    features2 = extract_features(source2, language)
    fp1 = normalize_conditions(normalize_loops(features1.fingerprint))
    fp2 = normalize_conditions(normalize_loops(features2.fingerprint))

    if not fp1 and not fp2:
        return 100.0

    if not fp1 or not fp2:
        return 0.0

    ratio = difflib.SequenceMatcher(None, fp1, fp2).ratio()
    return round(ratio * 100, 2)

if __name__ == "__main__":
    code_for = """
for i in range(10):
    print(i)
"""
    code_while = """
i = 0
while i < 10:
    print(i)
    i += 1
"""
    fp_for_raw = extract_features(code_for, "python").fingerprint
    fp_while_raw = extract_features(code_while, "python").fingerprint
    ratio_raw = difflib.SequenceMatcher(None, fp_for_raw, fp_while_raw).ratio()
    score_before = round(ratio_raw * 100, 2)
    score_after = compare_syntax(code_for, code_while, "python")
    
    print("=== Testing Loop Normalization ===")
    print(f"Similarity BEFORE normalization: {score_before}%")
    print(f"Similarity AFTER normalization: {score_after}%")
