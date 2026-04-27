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
class CFGFeatures:
    nodes: int = 0
    edges: int = 0
    cyclomatic_complexity: int = 0
    paths: int = 1
    loop_back_edges: int = 0
    condition_nodes: int = 0
    
    def to_vector(self) -> dict[str, float]:
        """Converts features into a numerical vector for cosine similarity."""
        return {
            "nodes": float(self.nodes),
            "edges": float(self.edges),
            "cyclomatic_complexity": float(self.cyclomatic_complexity),
            "paths": float(self.paths),
            "loop_back_edges": float(self.loop_back_edges),
            "condition_nodes": float(self.condition_nodes)
        }

class SimpleCFG:
    """
    A simplified representation of a Control Flow Graph.
    Instead of full basic block tracking, we extract the structural
    graph properties that are invariant to statement reordering.
    """
    def __init__(self):
        self.features = CFGFeatures()
        self.features.nodes = 2  
        self.features.edges = 1

def _build_python_cfg(source: str) -> SimpleCFG:
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Python SyntaxError: {e}")

    cfg = SimpleCFG()
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.stmt, ast.expr)):
            cfg.features.nodes += 1
            cfg.features.edges += 1
        if isinstance(node, ast.If):
            cfg.features.condition_nodes += 1
            cfg.features.edges += 1
            cfg.features.paths *= 2
        elif isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
            cfg.features.loop_back_edges += 1
            cfg.features.condition_nodes += 1
            cfg.features.edges += 2
            cfg.features.paths *= 2
        elif isinstance(node, (ast.Break, ast.Continue, ast.Return)):
            cfg.features.edges += 1
    cfg.features.cyclomatic_complexity = cfg.features.edges - cfg.features.nodes + 2
    return cfg

def _build_treesitter_cfg(source: str, language: str) -> SimpleCFG:
    try:
        parser = Parser(language=_TS_LANGUAGES[language])
        tree = parser.parse(bytes(source, "utf-8"))
    except Exception as e:
        raise ValueError(f"Tree-sitter failed to parse {language} source: {e}")

    cfg = SimpleCFG()
    
    def _walk(node):
        if node.is_named:
            cfg.features.nodes += 1
            cfg.features.edges += 1
            
            ntype = node.type
            if ntype in {"if_statement", "switch_statement", "conditional_expression"}:
                cfg.features.condition_nodes += 1
                cfg.features.edges += 1
                cfg.features.paths *= 2
            elif ntype in {"for_statement", "while_statement", "do_statement", "enhanced_for_statement"}:
                cfg.features.loop_back_edges += 1
                cfg.features.condition_nodes += 1
                cfg.features.edges += 2
                cfg.features.paths *= 2
            elif ntype in {"break_statement", "continue_statement", "return_statement"}:
                cfg.features.edges += 1
                
        for child in node.children:
            _walk(child)

    _walk(tree.root_node)
    cfg.features.cyclomatic_complexity = cfg.features.edges - cfg.features.nodes + 2
    return cfg

def build_cfg(source: str, language: str) -> SimpleCFG:
    """
    Builds a Control Flow Graph (CFG) for the given source code.
    Extracts nodes, edges, loops, and conditions based on the language.
    """
    lang = language.lower().strip()
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language '{language}'")
        
    if lang == "python":
        return _build_python_cfg(source)
    else:
        return _build_treesitter_cfg(source, lang)

def extract_cfg_features(cfg: SimpleCFG) -> CFGFeatures:
    """
    Extracts the analytical features of the Control Flow Graph.
    """
    return cfg.features

def _cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """Computes the cosine similarity between two feature vectors."""
    keys = set(vec1.keys()) | set(vec2.keys())
    if not keys:
        return 100.0

    dot = sum(vec1.get(k, 0.0) * vec2.get(k, 0.0) for k in keys)
    norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

    if norm1 == 0 and norm2 == 0:
        return 100.0
    if norm1 == 0 or norm2 == 0:
        return 0.0

    return (dot / (norm1 * norm2)) * 100.0

def compare_cfg(cfg1: SimpleCFG, cfg2: SimpleCFG) -> float:
    """
    Compares two CFGs using cosine similarity on their extracted features.
    Returns a score from 0.0 to 100.0.
    """
    feat1 = extract_cfg_features(cfg1).to_vector()
    feat2 = extract_cfg_features(cfg2).to_vector()
    
    return _cosine_similarity(feat1, feat2)

if __name__ == "__main__":
    code1 = '''
def process_number(x):
    if x > 0:
        result = x * 2
    else:
        result = x + 1
    return result
'''
    code2 = '''
def handle_number(x):
    if x <= 0:
        result = x + 1
    else:
        result = x * 2
    return result
'''

    print("=== Testing Control Flow Graph (CFG) Analysis ===")
    print("Case 1 - Same logic different order (Reordered branches)\\n")
    
    cfg1 = build_cfg(code1, "python")
    cfg2 = build_cfg(code2, "python")
    
    feat1 = extract_cfg_features(cfg1)
    feat2 = extract_cfg_features(cfg2)
    
    print(f"Features Code 1: {feat1}")
    print(f"Features Code 2: {feat2}\\n")
    
    score = compare_cfg(cfg1, cfg2)
    print(f"CFG Similarity Score: {score:.2f}%")
