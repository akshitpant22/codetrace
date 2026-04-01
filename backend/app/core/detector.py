import difflib
from typing import Dict, Any

from app.core.lexer import tokenize_code
from app.core.parser import compare_syntax
from app.core.semantic import compare_semantic


def calculate_lexical_similarity(tokens1: list[str], tokens2: list[str]) -> float:
    if not tokens1 and not tokens2:
        return 100.0
    if not tokens1 or not tokens2:
        return 0.0

    matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
    return round(matcher.ratio() * 100, 2)


def detect_plagiarism(source1: str, source2: str, language: str) -> Dict[str, Any]:
    tokens1 = tokenize_code(source1, language)
    tokens2 = tokenize_code(source2, language)
    lexical_score = calculate_lexical_similarity(tokens1, tokens2)

    syntax_score = compare_syntax(source1, source2, language)
    semantic_score = compare_semantic(source1, source2, language)

    # weights: lexical 20%, syntax 40%, semantic 40%
    final_score = (
        (lexical_score * 0.20) +
        (syntax_score * 0.40) +
        (semantic_score * 0.40)
    )

    return {
        "lexical_score":  lexical_score,
        "syntax_score":   syntax_score,
        "semantic_score": semantic_score,
        "final_score":    round(final_score, 2),
        "language":       language
    }
