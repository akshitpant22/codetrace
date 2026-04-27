import ast
import math
from dataclasses import dataclass

import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

_TS_LANGUAGES = {
    "c":    Language(tsc.language(), 'c'),
    "cpp":  Language(tscpp.language(), 'cpp'),
    "java": Language(tsjava.language(), 'java'),
}

SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java"}

@dataclass
class PDGFeatures:
    data_dependence_edges: int = 0
    control_dependence_edges: int = 0
    def_use_chains: int = 0
    dependency_depth: int = 0
    unique_vars: int = 0
    function_calls: int = 0
    return_statements: int = 0
    
    def to_vector(self) -> dict[str, float]:
        """Converts features into a numerical vector for cosine similarity."""
        return {
            "data_dependence_edges": float(self.data_dependence_edges),
            "control_dependence_edges": float(self.control_dependence_edges),
            "def_use_chains": float(self.def_use_chains),
            "dependency_depth": float(self.dependency_depth),
            "unique_vars": float(self.unique_vars),
            "function_calls": float(self.function_calls),
            "return_statements": float(self.return_statements)
        }

class SimplePDG:
    """
    A simplified Program Dependence Graph tracking definitions,
    uses, and control hierarchies to find semantic similarity.
    """
    def __init__(self):
        self.features = PDGFeatures()
        self.defined_vars = set()
        self.used_vars = set()
        self.var_depth = {}

def _build_python_pdg(source: str) -> SimplePDG:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Python SyntaxError: {e}")

    pdg = SimplePDG()
    
    def _walk(node, control_depth=0):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.Try)):
            body_stmts = sum(1 for child in ast.iter_child_nodes(node) if isinstance(child, list))
            pdg.features.control_dependence_edges += body_stmts * 2
            control_depth += 1
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            defs = []
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defs.append(target.id)
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                defs.append(node.target.id)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                defs.append(node.target.id)
                pdg.used_vars.add(node.target.id)
                pdg.features.data_dependence_edges += 1
                    
            for d in defs:
                pdg.defined_vars.add(d)
                if d not in pdg.var_depth:
                    pdg.var_depth[d] = 1

            val_node = node.value if hasattr(node, 'value') else None
            if val_node:
                for child in ast.walk(val_node):
                    if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                        used_var = child.id
                        pdg.used_vars.add(used_var)
                        
                        if used_var in pdg.defined_vars:
                            pdg.features.data_dependence_edges += 1
                            pdg.features.def_use_chains += 1
                            
                            new_depth = pdg.var_depth.get(used_var, 0) + 1
                            for d in defs:
                                pdg.var_depth[d] = max(pdg.var_depth.get(d, 1), new_depth)
                                pdg.features.dependency_depth = max(pdg.features.dependency_depth, pdg.var_depth[d])

        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            pdg.used_vars.add(node.id)
            if node.id in pdg.defined_vars:
                pdg.features.data_dependence_edges += 1
        elif isinstance(node, ast.Call):
            pdg.features.function_calls += 1
        elif isinstance(node, ast.Return):
            pdg.features.return_statements += 1

        for child in ast.iter_child_nodes(node):
            _walk(child, control_depth)

    _walk(tree)
    pdg.features.unique_vars = len(pdg.defined_vars.union(pdg.used_vars))
    return pdg

def _build_treesitter_pdg(source: str, language: str) -> SimplePDG:
    try:
        parser = Parser(language=_TS_LANGUAGES[language])
        tree = parser.parse(bytes(source, "utf-8"))
    except Exception as e:
        raise ValueError(f"Tree-sitter failed to parse {language} source: {e}")

    pdg = SimplePDG()
    
    def _walk(node, control_depth=0):
        if node.is_named:
            ntype = node.type
            if ntype in {"if_statement", "for_statement", "while_statement", "do_statement", "switch_statement"}:
                pdg.features.control_dependence_edges += len(node.children)
                control_depth += 1
            if ntype in {"assignment_expression", "variable_declarator"}:
                for child in node.children:
                    if child.type == "identifier":
                        var_name = child.text.decode("utf-8")
                        pdg.defined_vars.add(var_name)
                        pdg.used_vars.add(var_name)
                        pdg.features.data_dependence_edges += 1
                        pdg.features.def_use_chains += 1
                        
            elif ntype == "identifier":
                var_name = node.text.decode("utf-8")
                pdg.used_vars.add(var_name)
                
            elif ntype == "call_expression":
                pdg.features.function_calls += 1
            elif ntype == "return_statement":
                pdg.features.return_statements += 1
                
        for child in node.children:
            _walk(child, control_depth)

    _walk(tree.root_node)
    
    pdg.features.unique_vars = len(pdg.defined_vars.union(pdg.used_vars))
    pdg.features.dependency_depth = pdg.features.data_dependence_edges // 2
    
    return pdg

def build_pdg(source: str, language: str) -> SimplePDG:
    """
    Builds a Program Dependence Graph (PDG) for the given source code.
    Extracts data dependencies and control dependencies.
    """
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language '{language}'")
        
    if lang == "python":
        return _build_python_pdg(source)
    else:
        return _build_treesitter_pdg(source, lang)

def extract_pdg_features(pdg: SimplePDG) -> PDGFeatures:
    """
    Extracts the analytical features of the Program Dependence Graph.
    """
    return pdg.features

def _cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """Computes the raw cosine similarity between two feature vectors."""
    keys = set(vec1.keys()) | set(vec2.keys())
    if not keys:
        return 1.0

    dot = sum(vec1.get(k, 0.0) * vec2.get(k, 0.0) for k in keys)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

    if norm1 == 0 and norm2 == 0:
        return 1.0
    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)

def compare_pdg(pdg1: SimplePDG, pdg2: SimplePDG) -> float:
    """
    Compares two PDGs using cosine similarity on their extracted features.
    Applies strict structural and magnitude penalties to accurately reflect
    semantic differences in code logic.
    Returns a score from 0.0 to 100.0.
    """
    feat1 = extract_pdg_features(pdg1).to_vector()
    feat2 = extract_pdg_features(pdg2).to_vector()
    score = _cosine_similarity(feat1, feat2)
    norm1 = math.sqrt(sum(v ** 2 for v in feat1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in feat2.values()))
    if max(norm1, norm2) > 0:
        magnitude_ratio = min(norm1, norm2) / max(norm1, norm2)
        score *= (magnitude_ratio ** 2)
    d1 = feat1.get("data_dependence_edges", 0)
    c1 = feat1.get("control_dependence_edges", 0)
    ratio1 = d1 / (d1 + c1 + 1e-5)
    
    d2 = feat2.get("data_dependence_edges", 0)
    c2 = feat2.get("control_dependence_edges", 0)
    ratio2 = d2 / (d2 + c2 + 1e-5)
    
    edge_ratio_diff = abs(ratio1 - ratio2)
    score *= (1.0 - (edge_ratio_diff * 0.25))
    has_func1 = feat1.get("function_calls", 0) > 0
    has_func2 = feat2.get("function_calls", 0) > 0
    if has_func1 != has_func2:
        score *= 0.50
    has_ret1 = feat1.get("return_statements", 0) > 0
    has_ret2 = feat2.get("return_statements", 0) > 0
    if has_ret1 != has_ret2:
        score *= 0.50
        
    return max(0.0, score * 100.0)

if __name__ == "__main__":
    
    code1 = '''
def func1():
    x = 10
    y = x * 2
    z = y + 5
    return z
'''
    code2 = '''
def func2():
    a = 10
    b = a * 2
    c = b + 5
    return c
'''
    code3 = '''
def func3():
    name = "hello"
    greeting = name + " world"
    print(greeting)
'''

    print("=== Testing Program Dependence Graph (PDG) Analysis ===")
    
    print("\\nCase 1 - Same computation reordered/renamed (Expect HIGH similarity)")
    pdg1 = build_pdg(code1, "python")
    pdg2 = build_pdg(code2, "python")
    
    print(f"Features Code 1: {extract_pdg_features(pdg1)}")
    print(f"Features Code 2: {extract_pdg_features(pdg2)}")
    score1 = compare_pdg(pdg1, pdg2)
    print(f"PDG Similarity Score: {score1:.2f}%")

    print("\\nCase 2 - Different computation (Expect LOW similarity)")
    pdg3 = build_pdg(code3, "python")
    
    print(f"Features Code 1: {extract_pdg_features(pdg1)}")
    print(f"Features Code 3: {extract_pdg_features(pdg3)}")
    score2 = compare_pdg(pdg1, pdg3)
    print(f"PDG Similarity Score: {score2:.2f}%")
