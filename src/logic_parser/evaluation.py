from itertools import product

from lark import Lark, Token, Tree
from lark.visitors import Visitor

from logic_parser.utils import not_


class EvaluateFormula(Visitor):
    # transitive nodes are trees with a single child that
    # should receive the value of that single child
    transitive_nodes = {"formula", "start"}

    def __init__(self, valuation: dict[str, int], expr: str, *args, **kwargs):
        self.valuation = valuation
        self.result = [" " for _ in range(len(expr))]
        super().__init__(*args, **kwargs)

    def proposition(self, tree):
        letter: Token = tree.children[-1]
        evaluated = self.valuation[letter.value]
        if (negation := tree.children[0]).type == "NEGATION":
            setattr(tree, "v", not_(evaluated))
            self.result[negation.start_pos] = not_(evaluated)
        else:
            setattr(tree, "v", self.valuation[letter.value])

        self.result[letter.start_pos] = evaluated

    def composite(self, tree):
        op: Token = tree.children[1].children[0]
        lh, rh = tree.children[0].v, tree.children[2].v
        if op.type == "DISJUNCTION":
            evaluated = lh | rh
        elif op.type == "CONJUNCTION":
            evaluated = lh & rh
        elif op.type == "IMPLICATION":
            evaluated = not_(lh) | rh
        elif op.type == "EQUIVALENCE":
            evaluated = (lh & rh) | not_(lh | rh)
        else:
            raise ValueError(f"Unknown logical connective {op.type}")

        setattr(tree, "v", evaluated)
        self.result[op.start_pos] = evaluated

    def unary(self, tree):
        if (negation := tree.children[0]).type == "NEGATION":
            evaluated = not_(tree.children[1].v)
            setattr(tree, "v", evaluated)
            self.result[negation.start_pos] = evaluated
        elif tree.children[0].type == "proposition":
            # copy the value from the single proposition child
            setattr(tree, "v", not_(tree.children[0].v))

    @property
    def truth_table_entry(self) -> str:
        return "".join(map(str, self.result))

    def __default__(self, tree):
        if tree.data in self.transitive_nodes:
            setattr(tree, "v", tree.children[0].v)


class TruthTable:
    """Takes a correctly formatted propositional expression as a string
    and provides functionality for analyzing and evaluating (entries) of
    the truth-table."""

    def __init__(self, expr: str, grammar: str):
        self._expr = expr
        self._grammar = grammar
        self._propositions = None
        self._n_subformulas = None
        # the keys of `_truth_table` represent the valuation V
        # ordered by the alphabetical ordering (ASC) of the
        # corresponding proposition-letters.
        self._truth_table: dict[tuple[int], int] = {}
        # the `keys of _truth_table_entries` are the same as
        # for `_truth_table`. The values are lists of length len(`_expr`)
        # where each entry at index i is the evaluation of the subformula
        # at `_expr[i]`
        self._truth_table_entries: dict[tuple[int], list[int]] = {}
        self._tree = None
        self._is_tautology: bool | None = None
        self._is_contradiction: bool | None = None
        self._is_contingency: bool | None = None

    def __call__(self, v: dict[str, int]) -> int:
        """Evaluate `expr` for a given valuation `v`

        Parameters
        ----------
        v : dict
            the assignment of numbers to proposition letters
        """
        visitor = EvaluateFormula(v, self._expr)
        visitor.visit(self.parse_tree)
        result = self.parse_tree.v
        self[v] = (result, visitor.result)
        return result

    def _key(self, k: dict[str, int]) -> tuple[int]:
        return tuple(y[1] for y in sorted(k.items(), key=lambda x: x[0]))

    def __setitem__(self, v: dict[str, int], result: (int, list[str | int])):
        """Store the result `result` of evaluating `self._expr` with valuation `v`.

        Parameters
        ----------
        result : (int, list[str | int])
            the value of formula `_expr` after evaluating it for valuation `v` and
            the corresponding entry in the truth table

        """
        key = self._key(v)
        value, entry = result
        self._truth_table[key] = value
        self._truth_table_entries[key] = entry

    def __getitem__(self, v: dict[str, int]) -> int | None:
        key = self._key(v)
        return self._truth_table.get(key)

    def __str__(self):
        if not self._complete:
            self.construct()
        return "\n".join(
            [
                self._expr,
                *["".join(map(str, e)) for e in self._truth_table_entries.values()],
            ]
        )

    @property
    def is_tautology(self):
        if self._is_tautology is None:
            self.construct()
        return self._is_tautology

    @property
    def is_contradiction(self):
        if self._is_contradiction is None:
            self.construct()
        return self._is_contradiction

    @property
    def is_contingency(self):
        if self._is_contingency is None:
            self.construct()
        return self._is_contingency

    @property
    def parse_tree(self) -> Tree:
        if self._tree is None:
            parser = Lark(self._grammar)
            self._tree = parser.parse(self._expr)
        return self._tree

    @property
    def propositions(self):
        self.dimensions
        return self._propositions

    @property
    def n_subformulas(self):
        self.dimensions
        return self._n_subformulas

    @property
    def tt(self):
        if not self._complete:
            self.construct()
        return self._truth_table

    @property
    def dimensions(self) -> (int, int):
        """Retrieve the dimensions of the truth-table as rows x cols"""
        if not (
            self._propositions is None or self._n_subformulas is None
        ):  # (~p & ~q) = ~(p | q)
            return (2 ** len(self._propositions), self._n_subformulas)

        propositions, n_subformulas = set(), 0
        for e in self._expr:
            if e.isalpha():
                propositions |= {e}
                n_subformulas += 1
            if e in ["&", "|", ">", "=", "~"]:
                n_subformulas += 1
        self._propositions = propositions
        self._n_subformulas = n_subformulas
        return (2 ** len(propositions), n_subformulas)

    @property
    def _complete(self):
        num_rows, _ = self.dimensions
        return len(self._truth_table) == num_rows

    def construct(self):
        """Construct and return the complete truth table"""
        if self._complete:
            return self._truth_table

        ordered = sorted(self.propositions)
        n_propositions = len(ordered)
        is_tautology, is_contradiction = True, True
        for valuation in product(*[[0, 1] for _ in ordered]):
            assignment = {ordered[i]: valuation[i] for i in range(n_propositions)}
            result = self(assignment)
            is_tautology &= result
            is_contradiction &= not_(result)

        self._is_tautology = bool(is_tautology)
        self._is_contradiction = bool(is_contradiction)
        self._is_contingency = not is_contradiction and not is_tautology

        return self._truth_table
