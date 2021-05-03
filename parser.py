import token

from lexer import *
from utils import *
from elements import *


def strip_tokens(data, o_sequence, c_sequence, replacement=-1):
    """"strips function of brackets and replaces them with #"""
    fun_list = []
    l_indices = [i for i, ltr in enumerate(data) if o_sequence.__contains__(ltr)]
    r_indices = [i for i, ltr in enumerate(data) if c_sequence.__contains__(ltr)]
    f_list = []
    if len(l_indices) > 0:
        l_par_count = r_par_count = 1
        l_index = 0
        r_index = 0
        l_bound = l_indices[0]
        r_bound = r_indices[0]
        while l_par_count <= len(l_indices) or r_par_count <= len(r_indices):
            if l_par_count == r_par_count > 0 and (l_index + 1 == len(l_indices) or l_indices[l_index + 1] > r_bound):
                fun_list.append(data[l_bound: r_bound + 1])
                if l_par_count == len(l_indices) or r_par_count == len(r_indices):
                    break
                if l_index + 1 != len(l_indices):
                    l_index += 1
                    l_par_count = l_index + 1
                    r_index += 1
                    r_par_count = r_index + 1
                    l_bound = l_indices[l_index]
                    r_bound = r_indices[r_index]
                continue
            elif l_par_count < r_par_count:
                raise Exception("wrong order of opening and closing elements")
            if l_par_count < len(l_indices) and l_indices[l_index + 1] < r_indices[r_index]:
                l_index += 1
                l_par_count += 1
            elif r_par_count < len(r_indices):
                r_index += 1
                r_par_count += 1
                r_bound = r_indices[r_index]
        for s in fun_list:
            data = data.replace(s, replacement, 1)
        for s in fun_list:
            f_list.append(s[1: -1])
    return data, f_list


def dress_up_tokens(h_string_arr, inner, swap_char=-1):
    """"opposite of 'strip_functions' but returns array of functions, if used with'strip_functions' can separate
    comma separated functions"""
    function_arr = []
    count = 0
    for f in h_string_arr:
        fun = []
        for c in f:
            if c == swap_char:
                fun.append(inner[count])
                count += 1
            else:
                fun.append(c)
        function_arr.append(fun)
    return function_arr


def split_tokens(data, split_elem=token.SEMI):
    res = []
    split_points = [0] + [i+1 for i, j in enumerate(data) if j[0] == split_elem.value]
    for i in range(len(split_points) - 1):
        res.append(data[split_points[i]:split_points[i+1]])
    return res


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
        return match(matcher.copy().reverse(), pattern.copy().reverse(), True)
    return True


    # for i in range(1, end - pivot + 1):
    #     if pattern[-i][0] != matcher[-i].value:
    #         return False
    # return True


def build_single(seq):
    e = None
    # Initializer
    if match([token.NEW, token.TSTR, token.VNAME, token.SEMI], seq):
        e = Initializer(False, seq[2][1], len(seq[2][1]))
    elif match([token.NEW, token.TINT, token.VNAME, token.SEMI], seq):
        e = Initializer(True, seq[2][1], 4)
    elif match([token.NEW, token.TINT, token.OBR, (token.INT, token.VAR), token.CBR, token.VNAME, token.SEMI], seq):
        e = Initializer(True, seq[5][1], seq[3][1])
    # Assignment
    elif match([token.EXPR, token.VAR, (token.VAR, token.STR, token.INT), token.SEMI], seq):
        e = Assignment(seq[1][1], seq[2][1])
    # Expression
    elif match([token.EXPR, token.VAR, (token.VAR, token.INT), token.OP, (token.VAR, token.INT), token.SEMI], seq):
        e = Expression(seq[1][1], seq[2][1], seq[4][1], seq[3][1])
    #  If
    elif match([token.IF, token.VAR, token.OCBR, -1, token.CCBR, token.SEMI], seq):
        e = If(seq[1][1])
    #  While
    elif match([token.WHILE, token.VAR, token.OCBR, -1, token.CCBR, token.SEMI], seq):
        e = While(seq[1][1])
    #  Return
    elif match([token.RETURN, token.VAR], seq):
        e = Return(seq[1][1])
    #  Func
    elif len(seq) > 4 and match([token.INT], [seq[3]]) and match([token.FUNC, token.VAR, token.FNAME, token.INT] + \
                           [token.VNAME for i in range(int(seq[3]))] + [token.OCBR, -1, token.CCBR, token.SEMI], seq):
        e = Func(seq[2][1], seq[1][1], [i[1] for i in seq[4:4+seq[3][1]]])
    #  Call
    elif len(seq) >= 4 and match([token.INT], [seq[3]]) and match([token.CALL, token.VAR, token.FNAME] + \
                                 [(token.VAR, token.STR, token.INT) for i in range(len(seq - 4))] + [token.SEMI], seq):
        e = Call(seq[2][1], seq[1][1], [i[1] for i in seq[3:3+len(seq - 3)]])
    return e


def build(ctx, line):
    tok = -1
    f_data, f_list = strip_tokens(line, [token.OCBR], [token.CCBR], tok)
    f_data = split_tokens(f_data, token.SEMI)
    funs = dress_up_tokens(f_data, f_list, tok)
    for seq in funs:
        if (e := build_single(seq)) is not None:
            ctx.elem.append(e)
        else:
            raise Exception("unrecognized sequence")
    return True


# testing
if __name__ == "__main__":
    with open("source2") as f:
        lines = f.readlines()

    try:
        c = Context()
        for line in lines:
            while (tok_line := get_tok(line)) is None:
                pass
            if not build(c, tok_line):
                exit(1)
        c.execute()
    except Exception as e:
        print(f"ERROR:{e}")
    exit(0)
