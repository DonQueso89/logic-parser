import pytest

from logic_parser.evaluation import TruthTable


@pytest.mark.parametrize(
    "expr",
    [
        "p & q",
        "(p & q)",
        "p | q",
        "(p | q)",
        "p > q",
        "(p > q)",
        "p = q",
        "(p = q)",
        "~p = q",
        "(~p = q)",
        "p = ~q",
        "(~p = ~q)",
        "~(~p = ~q)",
        "~(p = q)",
        "~p = ~q",
        "~(p & q) | q",
        "(p & q) | q",
        "(p & q) > q",
        "(p & q) = ~q",
        "~(~p > ~q) = ~q",
        "~(~p > ~q) = ~(q | q)",
        "~(~p > ~q) = ~(q | ~q)",
        "~(p & q) = (~p | ~q)",  # DeMorgan
        "(p > q) = (~p | q)",  # Implication removal
        "(p & (p | q)) = p",  # Absorption
        "(p > q) = (~q > ~p)",  # Reverse implication
        "(~p & (q | p)) = ((~p & q) | (~p & p))",  # Distribution of & over |
        "(~p | (q & p)) = ((~p | q) & (~p | p))",  # Distribution of | over &
        "(p = q) = ((p > q) & (q > p))",
        "(p = q) = ((p & q) | (~p & ~q))",  # Equivalence removal
        "((p > q) & p) > q",  # Modus ponens
        "(p & q) > p",  # Conjunction removal
    ],
)
def test_parser_success(expr, grammar):
    TruthTable(expr, grammar).parse_tree
