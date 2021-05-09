from enum import Enum
import int_math as im


class token(Enum):
    IF = 0
    WHILE = 1
    FUNC = 2
    EXPR = 3
    CALL = 4
    RETURN = 5
    NEW = 6
    SEMI = 7
    TSTR = 8
    TINT = 9
    INT = 10
    STR = 11
    VNAME = 12
    FNAME = 13
    VAR = 14
    OP = 15
    OBR = 16
    CBR = 17
    OCBR = 18
    CCBR = 19
    NO = 20


int_math = {
    "+": im.add,
    "-": im.sub,
    "*": im.mul,
    "/": im.div,
    "%": im.mod,
    "~": im.spec,
}


def list_replace(list, target, replacement):
    for i in range(len(list) - len(target)):
        found = True
        for j in range(len(target)):
            if list[i+j] != target[j]:
                found = False
                break
        if found:
            list = list[:i] + replacement + list[i+len(target):]
            break
    return list


def strip_tokens(data, op, cl, replacement):
    """"strips token list of brackets and replaces them with replacement"""
    fun_list = []
    l_indices = [i+1 for i, ltr in enumerate(data) if op.value == ltr[0]]
    r_indices = [i-1 for i, ltr in enumerate(data) if cl.value == ltr[0]]
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
            if len(s) > 0:
                data = list_replace(data, s, [replacement])
                f_list.append(s)
                # f_list.append(s[1: -1])
    return data, f_list


def dress_up_tokens(h_string_arr, inner, swap_char=-1):
    """"opposite of 'strip_tokens' but returns array of functions, if used with'strip_tokens' can separate
    comma separated lines"""
    function_arr = []
    count = 0
    for f in h_string_arr:
        fun = []
        for c in f:
            if c == swap_char:
                if len(inner[count]) != 0:
                    fun = fun + inner[count]
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
