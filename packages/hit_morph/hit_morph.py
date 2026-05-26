from udapi.core.node import Node

def get_label(node: Node) -> str:
    if node.xpos:
        if node.upos:
            char = node.xpos[0]
            sep = '.' if char.isupper() or (char.isdigit() and not node.upos == 'DEM') else ''
            return sep.join([node.upos, node.xpos])
        else:
            return node.xpos
    else:
        if node.upos:
            return node.upos
        else:
            if node.gloss.startswith('CLF'):
                return node.gloss
            else:
                return '<ERR>'

