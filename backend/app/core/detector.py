from typing import Dict, Any

from app.core.lexer import compare_code_lexical
from app.core.parser import compare_syntax
from app.core.semantic import compare_semantic
from app.core.cfg import build_cfg, compare_cfg
from app.core.pdg import build_pdg, compare_pdg

def detect_plagiarism(source1: str, source2: str, language: str) -> Dict[str, Any]:
    """
    Runs a multi-layered plagiarism detection pipeline across 5 analysis stages.
    
    Weights:
    - Lexical (Winnowing Fingerprints): 15%
    - Syntax (Normalized AST comparison): 25%
    - Semantic (Metrics like Cyclomatic, Halstead, Entropy): 25%
    - CFG (Control Flow Graph execution paths): 20%
    - PDG (Program Dependence Graph data/control flow): 15%
    """
    lexical_score = compare_code_lexical(source1, source2, language)
    syntax_score = compare_syntax(source1, source2, language)
    semantic_score = compare_semantic(source1, source2, language)
    
    cfg1 = build_cfg(source1, language)
    cfg2 = build_cfg(source2, language)
    cfg_score = compare_cfg(cfg1, cfg2)
    
    pdg1 = build_pdg(source1, language)
    pdg2 = build_pdg(source2, language)
    pdg_score = compare_pdg(pdg1, pdg2)
    if lexical_score < 30.0 and cfg_score > 90.0:
        cfg_score *= 0.60
    final_score = (
        (lexical_score * 0.15) +
        (syntax_score * 0.20) +
        (semantic_score * 0.30) +
        (cfg_score * 0.20) +
        (pdg_score * 0.15)
    )
    if semantic_score < 40 and pdg_score < 40:
        final_score *= (max(semantic_score, pdg_score) / 100.0)
        
    final_score = round(final_score, 2)
    if final_score <= 30.0:
        verdict = "Not Plagiarized"
    elif final_score <= 70.0:
        verdict = "Possibly Plagiarized"
    else:
        verdict = "Plagiarized"

    return {
        "lexical_score":  lexical_score,
        "syntax_score":   syntax_score,
        "semantic_score": semantic_score,
        "cfg_score":      cfg_score,
        "pdg_score":      pdg_score,
        "final_score":    final_score,
        "verdict":        verdict
    }

if __name__ == "__main__":
    import json
    
    code_case1_a = """
def calculate(x, y):
    result = x + y
    return result
"""
    code_case1_b = """
def compute(a, b):
    total = a + b
    return total
"""
    code_case2_a = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
    code_case2_b = """
def analyze_numbers(nums):
    total = 0
    for n in nums:
        if n < 0:
            total += abs(n)
    return total
"""
    code_case3 = """
def greet(name):
    message = "Hello " + name
    print(message)
"""

    print("=== Testing Integrated Detection Pipeline ===")
    res1 = detect_plagiarism(code_case1_a, code_case1_b, "python")
    print(f"\nCase 1 - Same logic renamed (Expect >85%): {res1['final_score']}% -> {res1['verdict']}")
    print(json.dumps(res1, indent=2))
    res2 = detect_plagiarism(code_case2_a, code_case2_b, "python")
    print(f"\nCase 2 - Similar logic (Expect 40-70%): {res2['final_score']}% -> {res2['verdict']}")
    print(json.dumps(res2, indent=2))
    res3 = detect_plagiarism(code_case1_a, code_case3, "python")
    print(f"\nCase 3 - Completely different (Expect <20%): {res3['final_score']}% -> {res3['verdict']}")
    print(json.dumps(res3, indent=2))
