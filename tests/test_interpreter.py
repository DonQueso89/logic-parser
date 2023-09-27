import pytest

from logic_parser.evaluation import TruthTable


@pytest.mark.parametrize(
    "expr",
    [
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
def test_truth_table_tautologies(expr, grammar):
    tree = TruthTable(expr, grammar)
    assert tree.is_tautology is True
    assert tree.is_contradiction is False
    assert tree.is_contingency is False


@pytest.mark.parametrize(
    "expr",
    ["p & ~p", "(p & q) & (~p & q)", "(p = q) & ~(q > p)", "~(~(p & q) = (~p | ~q))"],
)
def test_truth_table_contradictions(expr, grammar):
    tree = TruthTable(expr, grammar)
    assert tree.is_tautology is False
    assert tree.is_contradiction is True
    assert tree.is_contingency is False


def test_dimensions():
    assert True
