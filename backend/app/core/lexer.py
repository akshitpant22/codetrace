import io
import hashlib
import tokenize as py_tokenize

import tree_sitter_c as tsc
import tree_sitter_cpp as tscpp
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser, Node

_PYTHON_SKIP_TYPES = {
    py_tokenize.COMMENT,
    py_tokenize.NEWLINE,
    py_tokenize.NL,
    py_tokenize.INDENT,
    py_tokenize.DEDENT,
    py_tokenize.ENCODING,
    py_tokenize.ENDMARKER,
}

_TS_LANGUAGES = {
    "c":    Language(tsc.language(), 'c'),
    "cpp":  Language(tscpp.language(), 'cpp'),
    "java": Language(tsjava.language(), 'java'),
}

_TS_COMMENT_NODES = {
    "c":    {"comment"},
    "cpp":  {"comment"},
    "java": {"line_comment", "block_comment"},
}

SUPPORTED_LANGUAGES = {"python", "c", "cpp", "java"}

def _normalize_identifier(name, var_map, func_map, var_counter, func_counter, is_function=False):
    if is_function:
        if name not in func_map:
            func_counter[0] += 1
            func_map[name] = f"func{func_counter[0]}"
        return func_map[name]
    else:
        if name not in var_map:
            var_counter[0] += 1
            var_map[name] = f"var{var_counter[0]}"
        return var_map[name]

def _tokenize_python(source: str) -> list[str]:
    tokens = []
    var_map: dict = {}
    func_map: dict = {}
    var_counter = [0]
    func_counter = [0]

    try:
        raw_tokens = list(py_tokenize.generate_tokens(io.StringIO(source).readline))
    except py_tokenize.TokenError:
        raw_tokens = []

    for i, tok in enumerate(raw_tokens):
        tok_type, tok_string = tok.type, tok.string

        if tok_type in _PYTHON_SKIP_TYPES:
            continue

        if tok_type == py_tokenize.NAME:
            import keyword
            if keyword.iskeyword(tok_string) or keyword.issoftkeyword(tok_string):
                tokens.append(tok_string)
                continue

            is_func = (i + 1 < len(raw_tokens) and raw_tokens[i + 1].string == "(")
            normalized = _normalize_identifier(
                tok_string, var_map, func_map,
                var_counter, func_counter,
                is_function=is_func,
            )
            tokens.append(normalized)

        elif tok_type == py_tokenize.NUMBER:
            tokens.append("NUMBER")

        elif tok_type == py_tokenize.STRING:
            tokens.append("STRING")

        elif tok_type == py_tokenize.OP:
            tokens.append(tok_string)

    return tokens

def _walk_tree(node: Node):
    if len(node.children) == 0:
        yield node
    else:
        for child in node.children:
            yield from _walk_tree(child)

def _tokenize_treesitter(source: str, language: str) -> list[str]:
    comment_nodes = _TS_COMMENT_NODES.get(language, set())

    try:
        parser = Parser(language=_TS_LANGUAGES[language])
        tree = parser.parse(bytes(source, "utf-8"))
    except Exception as e:
        raise ValueError(f"Tree-sitter failed to parse {language} source: {e}")

    tokens = []
    var_map: dict = {}
    func_map: dict = {}
    var_counter = [0]
    func_counter = [0]

    leaf_nodes = list(_walk_tree(tree.root_node))

    for i, node in enumerate(leaf_nodes):
        node_type = node.type
        text = node.text.decode("utf-8").strip()

        if not text:
            continue

        if node_type in comment_nodes:
            continue

        if node_type == "identifier":
            is_func = (i + 1 < len(leaf_nodes) and leaf_nodes[i + 1].type == "(")
            normalized = _normalize_identifier(
                text, var_map, func_map,
                var_counter, func_counter,
                is_function=is_func,
            )
            tokens.append(normalized)

        elif node_type in {"number_literal", "integer_literal",
                           "floating_point_literal", "decimal_integer_literal",
                           "hex_integer_literal"}:
            tokens.append("NUMBER")

        elif node_type in {"string_literal", "character_literal", "string_content"}:
            tokens.append("STRING")

        else:
            tokens.append(text)

    return tokens

def tokenize_code(source: str, language: str) -> list[str]:
    lang = language.lower().strip()

    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language '{language}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
        )

    if lang == "python":    
        return _tokenize_python(source)
    else:
        return _tokenize_treesitter(source, lang)

def winnowing_fingerprint(tokens: list[str], window_size: int = 5) -> set[int]:
    """
    Applies the Winnowing algorithm to create a fingerprint of the code.
    1. Creates k-grams (sequences of tokens) to capture context.
    2. Hashes each k-gram.
    3. Creates a rolling window over the hashes.
    4. Selects the minimum hash in each window to form the fingerprint.
    """
    k_gram_size = window_size
    
    if len(tokens) < k_gram_size:
        if not tokens:
            return set()
        return {int(hashlib.md5("".join(tokens).encode()).hexdigest(), 16)}
    k_grams = []
    for i in range(len(tokens) - k_gram_size + 1):
        k_gram_string = "".join(tokens[i:i + k_gram_size])
        k_gram_hash = int(hashlib.md5(k_gram_string.encode()).hexdigest(), 16)
        k_grams.append(k_gram_hash)
    fingerprint = set()
    if len(k_grams) < window_size:
        fingerprint.add(min(k_grams))
        return fingerprint
    for i in range(len(k_grams) - window_size + 1):
        window = k_grams[i:i + window_size]
        fingerprint.add(min(window))
        
    return fingerprint

def compare_fingerprints(fp1: set[int], fp2: set[int]) -> float:
    """
    Compares two fingerprint sets using the Jaccard similarity index.
    Formula: (Intersection / Union) * 100
    Returns a score from 0.0 to 100.0.
    """
    if not fp1 and not fp2:
        return 100.0
    if not fp1 or not fp2:
        return 0.0
        
    intersection = len(fp1.intersection(fp2))
    union = len(fp1.union(fp2))
    
    return (intersection / union) * 100.0

def compare_code_lexical(source1: str, source2: str, language: str) -> float:
    """
    Main lexer comparison function using Winnowing.
    Tokenizes both source codes, generates Winnowing fingerprints,
    and returns the Jaccard similarity score.
    """
    tokens1 = tokenize_code(source1, language)
    tokens2 = tokenize_code(source2, language)
    
    fp1 = winnowing_fingerprint(tokens1)
    fp2 = winnowing_fingerprint(tokens2)
    
    return compare_fingerprints(fp1, fp2)

if __name__ == "__main__":
    code1 = '''
def calculate_sum(a, b):
    return a + b
'''
    code2 = '''
def add_nums(x, y):
    result = x + y
    return result
'''
    
    print("=== Testing Winnowing Algorithm ===")
    print(f"Code 1: {code1.strip()}")
    print("-" * 30)
    print(f"Code 2: {code2.strip()}")
    print("-" * 30)
    
    t1 = tokenize_code(code1, "python")
    t2 = tokenize_code(code2, "python")
    
    print(f"Tokens 1 ({len(t1)}): {t1}")
    print(f"Tokens 2 ({len(t2)}): {t2}")
    
    fp1 = winnowing_fingerprint(t1)
    fp2 = winnowing_fingerprint(t2)
    
    print(f"Fingerprint 1 size: {len(fp1)}")
    print(f"Fingerprint 2 size: {len(fp2)}")
    
    score = compare_code_lexical(code1, code2, "python")
    print(f"Jaccard Similarity Score: {score:.2f}%")
