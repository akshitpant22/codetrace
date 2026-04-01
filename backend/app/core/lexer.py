import io
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
    "c":    Language(tsc.language()),
    "cpp":  Language(tscpp.language()),
    "java": Language(tsjava.language()),
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
