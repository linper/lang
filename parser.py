import sys
import token
from lexer import *
from utils import *
from elements import *


def match(matcher, pattern, reversed=False):
    pivot = end = len(matcher)
    if -1 in matcher:
        pivot = matcher.index(-1)
    for i in range(pivot):
        if isinstance(matcher[i], tuple):
            found = False
            for m in matcher[i]:
                if pattern[i][0] != m.value:
                    found = True
            if not found:
                return False
        elif pattern[i][0] != matcher[i].value:
            return False
    if pivot != end and not reversed:
        m_cpy = matcher.copy()
        m_cpy.reverse()
        p_cpy = pattern.copy()
        p_cpy.reverse()
        return match(m_cpy, p_cpy, True)
    return True


def build_single(seq, ctx):
    e = None
    b = None
    # Initializer
    if match([token.NEW, token.TSTR, token.VNAME, token.SEMI], seq):
        e = Initializer(ctx, False, seq[2], (token.INT, 4))
    elif match([token.NEW, token.TINT, token.VNAME, token.SEMI], seq):
        e = Initializer(ctx, True, seq[2], (token.INT, 4))
    elif match([token.NEW, token.TINT, token.OBR, (token.INT, token.VAR), token.CBR, token.VNAME, token.SEMI], seq):
        e = Initializer(ctx, True, seq[5], seq[3])
    # Assignment
    elif match([token.EXPR, token.VAR, (token.VAR, token.STR, token.INT), token.SEMI], seq):
        e = Assignment(ctx, seq[1], seq[2])
    # Expression
    elif match([token.EXPR, token.VAR, (token.VAR, token.INT), token.OP, (token.VAR, token.INT), token.SEMI], seq):
        e = Expression(ctx, seq[1], seq[2], seq[4], seq[3])
    #  If
    elif match([token.IF, token.VAR, token.OCBR, -1, token.CCBR, token.SEMI], seq):
        e = If(ctx, seq[1])
        b = seq[3:len(seq)-2]
    #  While
    elif match([token.WHILE, token.VAR, token.OCBR, -1, token.CCBR, token.SEMI], seq):
        e = While(ctx, seq[1])
        b = seq[3:len(seq)-2]
    #  Return
    elif match([token.RETURN, token.VAR, token.SEMI], seq):
        e = Return(ctx, seq[1])
    #  Print
    elif match([token.PRINT, (token.VAR, token.STR, token.INT), token.SEMI], seq):
        e = Print(ctx, seq[1])
    #  Func
    elif len(seq) > 4 and match([token.INT], [seq[2]]) and match([token.FUNC, token.FNAME, token.INT] + \
                           [token.VNAME for i in range(int(seq[2][1]))] + [token.OCBR, -1, token.CCBR, token.SEMI], seq):
        e = Func(ctx, seq[1], [i for i in seq[3:3+int(seq[2][1])]])
        b = seq[4+int(seq[2][1]):len(seq)-2]
    #  Call
    elif len(seq) >= 4 and match([token.CALL, token.VAR, token.FNAME] + \
                                 [(token.VAR, token.STR, token.INT) for i in range(len(seq) - 4)] + [token.SEMI], seq):
        e = Call(ctx, seq[2], seq[1], [i for i in seq[3:3+len(seq) - 4]])
    return e, b


def build(ctx, line):
    tok = (-1, '')
    f_data, f_list = strip_tokens(line, token.OCBR, token.CCBR, tok)
    f_data = split_tokens(f_data, token.SEMI)
    funs = dress_up_tokens(f_data, f_list, tok)
    for seq in funs:
        e, b = build_single(seq, ctx)
        if e is not None:
            if b is not None and len(b) > 0:
                cb = ctx.cur_block
                ctx.cur_block = e.block
                build(ctx, b)
                ctx.cur_block = cb
        else:
            raise Exception("unrecognized sequence")
    return True


if __name__ == "__main__":
    is_interactive = True
    source_file = ""
    argi = 1
    while argi < len(sys.argv):
        if sys.argv[argi] == "-i":
            is_interactive = True
        elif sys.argv[argi] == "-f":
            is_interactive = False
            source_file = sys.argv[argi+1]
            argi += 1
        else:
            print("Unsupported argument")
        argi += 1

    ctx = Context()
    if not is_interactive:
        with open(source_file) as f:
            lines = f.readlines()
        try:
            for line in lines:
                if (tok_line := get_tok(line)) is None:
                    continue
                if tok_line[0] == token.NO:
                    continue
                if not build(ctx, tok_line):
                    exit(1)
            ctx.execute()
        except Exception as e:
            print(f"ERROR:{e}")
            exit(1)
    else:
        while True:
            line = input()
            try:
                if (tok_line := get_tok(line)) is None:
                    continue
                if tok_line[0] == token.NO:
                    continue
                if not build(ctx, tok_line):
                    exit(1)
                ctx.execute()
            except Exception as e:
                print(f"ERROR:{e}")
    exit(0)
