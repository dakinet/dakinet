"""Minimalni S-expression parser/pisac za KiCad fajlove (.kicad_sym, .kicad_sch)."""
import re

_TOK = re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))', re.S)
_ESC = re.compile(r'\\(.)')


class Sym(str):
    """Neocitirani atom (ključna reč ili broj)."""


def parse(text):
    stack, cur = [], []
    for m in _TOK.finditer(text):
        lp, rp, st, at = m.groups()
        if lp:
            stack.append(cur)
            cur = []
        elif rp:
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif st is not None:
            cur.append(_ESC.sub(lambda m: {'n': '\n'}.get(m.group(1), m.group(1)), st[1:-1]))
        elif at is not None:
            cur.append(Sym(at))
    return cur[0]


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def dump(x, ind=0):
    if isinstance(x, list):
        if not x:
            return '()'
        if all(not isinstance(i, list) for i in x):
            return '(' + ' '.join(dump(i) for i in x) + ')'
        s = '(' + dump(x[0])
        for i in x[1:]:
            if isinstance(i, list):
                s += '\n' + '\t' * (ind + 1) + dump(i, ind + 1)
            else:
                s += ' ' + dump(i)
        return s + ')'
    if isinstance(x, Sym):
        return str(x)
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    if isinstance(x, (int, float)):
        v = round(float(x), 4)
        return ('%d' % v) if v == int(v) else ('%g' % v)
    return q(x)


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def first(node, key):
    r = find(node, key)
    return r[0] if r else None
