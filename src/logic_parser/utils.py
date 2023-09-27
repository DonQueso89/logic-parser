from pathlib import Path


def not_(b: 0 | 1) -> [0 | 1]:
    return (b - 1) * -1


def get_grammar(grammar_path: Path | str) -> str:
    grammar_path = Path(grammar_path)
    with open(grammar_path) as fp:
        grammar = fp.read()
    return grammar
