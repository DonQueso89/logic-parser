#!/usr/bin/env python

import argparse
from pathlib import Path

from lark import Tree, Token

from logic_parser.evaluation import TruthTable
from logic_parser.transformation import DNFTransformer
from logic_parser.utils import get_grammar

err_msg = "A valuation must define 1 or 0 for all propositions in the expression"


class ItemsToDictAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        tt = TruthTable(namespace.expr, get_grammar(namespace.grammar_file))
        propositions = tt.propositions
        items = {}
        for item in values:
            letter, value = item.split("=")

            if value not in ["0", "1"]:
                raise ValueError(err_msg)

            items[letter] = int(value)

        if len(propositions & set(items)) != len(propositions):
            raise ValueError(err_msg)

        setattr(namespace, self.dest, items)


argparser = argparse.ArgumentParser()
argparser.add_argument("expr")
argparser.add_argument(
    "--grammar-file",
    "-g",
    help="absolute or relative path (from cwd) to grammar file",
    default="./grammar",
)
argparser.add_argument(
    "--eval",
    "-e",
    dest="valuation",
    nargs="*",
    help="Evaluate the expression for the given valuation",
    action=ItemsToDictAction,
)
argparser.add_argument(
    "--tt", "-t", action="store_true", help="Output a truth table for the expression"
)
argparser.add_argument(
    "--dnf", "-d", action="store_true", help="Output a disjunctive normal form"
)

"""
Features:

- reduce to disjunctive normal form (with operations displayed)
- reduce to conjunctive normal form (with operations displayed)
"""

def expr_from_tree(tree: Tree) -> str:
    tokens = list(tree.scan_values(lambda t: isinstance(t, Token)))
    s = [" " for _ in range(max(tokens, key=lambda t: t.start_pos).start_pos + 1)]
    for t in tokens:
        s[t.start_pos] = t.value
    return "".join(s)

def run(
    truth_table: TruthTable,
    valuation: dict | None = None,
    output_tt: bool = False,
    output_dnf: bool = False
):
    """
    Parameters
    ----------
    output_tt : bool, optional
        Write a formatted truth-table for `expr` to stdout
    """
    if valuation:
        result = truth_table(valuation)
        print(f"F({valuation}) = {result}")

    if output_tt:
        print(truth_table)
        if truth_table.is_tautology:
            print("This formula is a tautology")
        if truth_table.is_contradiction:
            print("This formula is a contradiction")
    
    if output_dnf:
        transformer = DNFTransformer()
        print(truth_table.parse_tree.pretty())
        dnf_tree = transformer.transform(truth_table.parse_tree)
        print(dnf_tree.pretty())
        print(expr_from_tree(dnf_tree))
        print(expr_from_tree(truth_table.parse_tree))


def main():
    args = argparser.parse_args()

    grammar = get_grammar(args.grammar_file)
    truth_table = TruthTable(args.expr, grammar)
    # parse early so we fail fast
    truth_table.parse_tree
    run(
        truth_table,
        valuation=args.valuation,
        output_tt=args.tt,
        output_dnf=args.dnf
    )
