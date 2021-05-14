import numpy as np
import copy

to_hex = {
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "A",
    11: "B",
    12: "C",
    13: "D",
    14: "E",
    15: "F",
}


def bt_arr_to_hex(arr):
    hex_arr = []
    for b in arr:
        hex_arr.append(to_hex.get(b // 16))
        hex_arr.append(to_hex.get(b % 16))
    return hex_arr


def _str_to_dec_bt_arr(_str):
    arr = []
    for s in _str:
        arr.append(int(s))
    return arr


def _lshift_add(arr, tail=0):
    for i in range(len(arr)-1):
        arr[i] = arr[i+1]
    arr[-1] = tail
    return arr


def _bt_more_or_equal(a, b):
    a_st = 0
    b_st = 0
    for i, bt in enumerate(a):
        if bt != 0:
            a_st = i - len(a)
            break
    for i, bt in enumerate(b):
        if bt != 0:
            b_st = i - len(b)
            break
    st = min(a_st, b_st)
    if abs(st) > len(a):
        return False
    if abs(st) > len(b):
        return True
    while st < 0:
        if a[st] > b[st]:
            return True
        if a[st] < b[st]:
            return False
        st += 1
    return True


def _get_rem(arr):
    div = []
    val = 0
    start = False
    for a in arr: # TODO might fail later
        val = (10 * val + a)
        if start or val >= 256:
            div.append(val // 256)
            start = True
        val %= 256
    return div, val


def str_to_bt_arr(str, length):
    bt_arr = bytearray(length)
    dec_arr = _str_to_dec_bt_arr(str)
    bt_count = -1
    while len(dec_arr) > 0 and -bt_count <= length:
        dec_arr, rem = _get_rem(dec_arr)
        bt_arr[bt_count] = rem
        bt_count -= 1
    return bt_arr


def naive_bt_div(a, b):
    val = 0
    while _bt_more_or_equal(a, b):
        a = sub2(a, b)
        val += 1
    return val, a


def str_to_bt_arr2(_str):
    if isinstance(_str, bytearray):
        return _str
    if isinstance(_str, int):
        _str = str(_str)
    bt_list = []
    dec_arr = _str_to_dec_bt_arr(_str)
    bt_count = -1
    while len(dec_arr) > 0:
        dec_arr, rem = _get_rem(dec_arr)
        bt_list.append(rem)
        bt_count -= 1
    bt_arr = bytearray(len(bt_list))
    for i, b in enumerate(reversed(bt_list)):
        bt_arr[i] = b
    return bt_arr


def bt_arr_to_int(arr):
    val = 0
    for i, b in enumerate(reversed(arr)):
        val += (256 ** i) * b
    return val


def _add_multi_arr(arr):
    rem = 0
    res = bytearray(len(arr[0]))
    for i in range(1, len(arr[0])+1):
        sum = np.sum([a[-i] for a in arr]) + rem
        res[-i] = sum % 256
        rem = sum // 256
    return res


def _add_single(a, b, rem):
    c = a+b+rem
    return c % 256, c // 256


def _sub_single(a, b, rem):
    c = a+rem-b
    rem = 0
    if c < 0:
        c += 256
        rem = -1
    return c, rem


def _mul_single(a, b, rem):
    c = a*b+rem
    return c % 256, c // 256


def clear_bt_arr(data):
    for i in range(len(data)):
        data[i] = 0


def add(r, a, b):
    r_len = r.length
    a_len = len(a)
    b_len = len(b)
    _a = 0
    _b = 0
    i = 1
    rem = 0
    res_arr = copy.copy(r.data)
    clear_bt_arr(res_arr)
    while i < r_len:
        if i > a_len:
            _a = 0
        else:
            _a = a[-i]
        if i > b_len:
            _b = 0
        else:
            _b = b[-i]
        el, rem = _add_single(_a, _b, rem)
        res_arr[-i] = el
        i += 1
    r.data = res_arr


def sub(r, a, b):
    r_len = r.length
    a_len = len(a)
    b_len = len(b)
    _a = 0
    _b = 0
    i = 1
    rem = 0
    res_arr = copy.copy(r.data)
    clear_bt_arr(res_arr)
    while i < r_len:
        if i > a_len:
            _a = 0
        else:
            _a = a[-i]
        if i > b_len:
            _b = 0
        else:
            _b = b[-i]
        el, rem = _sub_single(_a, _b, rem)
        res_arr[-i] = el
        i += 1
    r.data = res_arr


def sub2(a, b):
    r = bytearray(len(a))
    r_len = len(r)
    a_len = len(a)
    b_len = len(b)
    _a = 0
    _b = 0
    i = 1
    rem = 0
    clear_bt_arr(r)
    while i < r_len:
        if i > a_len:
            _a = 0
        else:
            _a = a[-i]
        if i > b_len:
            _b = 0
        else:
            _b = b[-i]
        el, rem = _sub_single(_a, _b, rem)
        r[-i] = el
        i += 1
    return r


def mul(r, a, b):
    res_arr = copy.copy(r.data)
    clear_bt_arr(res_arr)
    r_len = r.length
    a_cp = bytearray(r_len)
    a_cp[r_len - len(a):] = a
    a_len = len(a_cp)
    add_arr = []
    _a = 0
    i = 1
    rem = 0
    for j, m in enumerate(reversed(b)):
        arr = bytearray(r_len)
        while i < r_len:
            if i >= a_len:
                _a = 0
            else:
                _a = a_cp[-i]
            el, rem = _mul_single(_a, m, rem)
            arr[-i] = el
            i += 1
        add_arr.append(arr)
        i = 1
        a_cp = _lshift_add(a_cp, 0)
    r.data = _add_multi_arr(add_arr)


def div(r, a, b):
    res_arr = copy.copy(r.data)
    clear_bt_arr(res_arr)
    rem = copy.copy(r.data)
    clear_bt_arr(rem)
    val = []
    for _a in a:
        rem = _lshift_add(rem, _a)
        v, rem = naive_bt_div(rem, b)
        val.append(v)
    for i, _b in enumerate(reversed(val)):
        res_arr[-i-1] = _b
    r.data = res_arr


def mod(r, a, b):
    rem = copy.copy(r.data)
    clear_bt_arr(rem)
    for _a in a:
        rem = _lshift_add(rem, _a)
        v, rem = naive_bt_div(rem, b)
    r.data = rem


# r = max(0, a-b)
def spec(r, a, b):
    r_len = r.length
    a_len = len(a)
    b_len = len(b)
    if r_len < a_len or r_len < b_len:
        raise Exception(f"not enough space in {r.name}")
    max_in_len = max(a_len, b_len)
    _a = 0
    _b = 0
    i = 1
    rem = 0
    res_arr = copy.copy(r.data)
    clear_bt_arr(res_arr)
    while i < max_in_len:
        if i > a_len:
            _a = 0
        else:
            _a = a[-i]
        if i > b_len:
            _b = 0
        else:
            _b = b[-i]
        el, rem = _sub_single(_a, _b, rem)
        res_arr[-i] = el
        i += 1
    if rem < 0:
        for i in range(len(res_arr)):
            res_arr[i] = 0
    r.data = res_arr


