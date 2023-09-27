from lark import Transformer, Tree, Token

def de_morgan(tree: Tree):
    if not isinstance(tree, Tree) or tree.data != "composite":
        raise ValueError("Can only apply DeMorgan on 'composite' Tree")
    operator = tree.children[1].children[0]

    if operator.value == "|" :
        operator = Tree(Token('RULE', 'op'), [Token('CONJUNCTION', '&')])
    elif operator.value == '&':
        operator = Tree(Token('RULE', 'op'), [Token('DISJUNCTION', '|')])
    else:
        raise ValueError("Can only apply DeMorgan on '&' or '|' Tree")
    lh, rh = tree.children[0], tree.children[2]
    for operand in [lh, rh]:
        if operand.data == "proposition":
            operand.children.insert(0, Token('NEGATION', '~'))

    return Tree("composite", [lh, operator, rh])

class DNFTransformer(Transformer):
    """
    Traverse a parse-tree depth first and perform the following
    transformations:

     - formulas of the form '~(p & q)' into '~p | ~q'
     - formulas of the form '~(p | q)' into '~p & ~q'
     - formulas of the form 'p > q' into '~p | q'
     - formulas of the form 'p & (q | r)' into '(p & q) | (p & r)'

    until it reaches a Disjunctive Normal Form (DNF).

    """
    def __init__(self):
        super().__init__(visit_tokens=False)

    def unary(self, args):
        """
        The rules in the current grammar that are eligible for
        deMorgan are always of type 'unary'
        """
        if isinstance(args[0], Token) and args[0].type == "NEGATION":
            return de_morgan(args[1])
        elif isinstance(args[0], Tree) and args[0].data == "proposition":
            print(args[0].data)
        else:
            raise ValueError(f"{args} is an unknown unary rule")

        return Tree("unary", args)
