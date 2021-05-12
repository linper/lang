from utils import *
from int_math import *


class Context:
    def __init__(self):
        # list of dicts of local vars; key - name
        # should be used as stack
        # we have no global variables
        # only last element's scope is visible
        self.loc = [{}]
        # dict of functions; key - name
        self.fun = {}
        # list of callable elements
        self.elem = []
        # list of elements in current block(if, while, function or global) important when building
        self.cur_block = self.elem
        self.fun_ret = None

    def clear(self):
        self.loc = [{}]
        self.fun = {}
        self.elem = []

    def execute(self):
        for e in self.elem:
            e(self)

    def get_value(self, data):
        if data[0] == token.VAR.value:
            if self.loc[-1].get(data[1]) is None:
                raise Exception(f"variable: {data[1]}, does not exists")
            return self.loc[-1].get(data[1]).data
        return str_to_bt_arr2(data[1])

    def get_var(self, name):
        if self.loc[-1].get(name[1]) is None:
            raise Exception(f"variable: {name[1]}, does not exists")
        return self.loc[-1].get(name[1])

    def get_fun(self, name):
        if self.fun.get(name[1]) is None:
            raise Exception(f"function: {name[1]}, is not declared")
        return self.fun[name[1]]

    def assert_not_exist(self, data):
        if data[0] in [token.VAR.value, token.VNAME.value]:
            if self.loc[-1].get(data[1]) is not None:
                raise Exception(f"variable: {data[1]}, already exists")

    def assert_exist(self, data):
        if data[0] in [token.VAR.value, token.VNAME.value]:
            if self.loc[-1].get(data[1]) is None:
                raise Exception(f"variable: {data[1]}, does not exists")

    def check_exist(self, data):
        return self.loc[-1].get(data[1]) is not None

    def set_fun(self, fun):
        if self.fun.get(fun.name[1]) is not None:
            raise Exception(f"function: {fun.name[1]}, already declared")
        self.fun[fun.name[1]] = fun

    def set_var(self, var):
        self.loc[-1][var.name] = var

    def set_var2(self, name):
        self.loc[-1][name] = None

    def set_var3(self, name, var):
        self.loc[-1][name[1]] = var


class Var:
    def __init__(self, is_int, name, length):
        self.is_int = is_int
        self.length = length
        self.name = name
        self.data = None


class Initializer:
    def __init__(self, ctx, is_int, name, length):
        self.is_int = is_int
        self.name = name
        self.length = length
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        ctx.assert_not_exist(self.name)
        name = self.name[1]
        length = bt_arr_to_int(ctx.get_value(self.length))
        if isinstance(length, bytearray):
            length = bt_arr_to_int(length)
        elif isinstance(length, str):
            length = int(length)
        var = Var(self.is_int, name, length)
        var.data = bytearray(length)
        ctx.set_var(var)


class Assignment:
    def __init__(self, ctx, name, value):
        self.name = name
        self.value = value
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        var = ctx.get_var(self.name)
        if var.is_int:
            if self.value[0] == token.VAR.value:
                nv = ctx.get_value(self.value)
                clear_bt_arr(var.data)
                for i in range(1, min(len(nv), len(var.data))+1):
                    var.data[-i] = nv[-i]
            else:
                var.data = str_to_bt_arr(self.value[1], var.length)
        else:
            if len(self.name) > var.length:
                raise Exception(f"out of bounds for: {self.name}, with: {self.value}")
            var.data = bytearray(self.value[1], "utf-8")


class Expression:
    def __init__(self, ctx, result, first, second, expr):
        self.result = result
        self.first = first
        self.second = second
        self.expr = expr
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        result = ctx.get_var(self.result)
        first = ctx.get_value(self.first)
        second = ctx.get_value(self.second)
        int_math[self.expr[1]](result, first, second)


class If:
    def __init__(self, ctx, cond):
        self.cond = cond
        self.block = []
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        cond = ctx.get_var(self.cond)
        if bt_arr_to_int(cond.data) != 0:
            for e in self.block:
                e(ctx)
                if isinstance(e, Return):
                    ctx.fun_ret = e
                    break


class While:
    def __init__(self, ctx, cond):
        self.cond = cond
        self.block = []
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        cond = ctx.get_var(self.cond)
        while bt_arr_to_int(cond.data) != 0:
            for e in self.block:
                e(ctx)
                if isinstance(e, Return):
                    ctx.fun_ret = e
                    break


class Func:
    def __init__(self, ctx, name, args):
        self.name = name
        self.stack_frame = {}  # varnames as ctx.loc[-1] keys
        self.args = args  # varnames
        self.arg_len = len(args)
        self.block = []
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        ctx.set_fun(self)
        # for a in self.args:
        #     ctx.set_var2(a[1])

        # for a in self.args:
        #     self.stack_frame[a] = None
        # if ctx.fun.get(self.name) is not None:
        #     raise Exception(f"function: {self.name}, already declared")
        # ctx.fun[self.name] = self
        # ctx.cur_block.append(self)
        # ctx.cur_block = self.block


class Return:
    def __init__(self, ctx, variable):
        self.variable = variable
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        ctx.assert_exist(self.variable)


class Print:
    def __init__(self, ctx, variable):
        self.variable = variable
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        val = []
        if ctx.check_exist(self.variable):
            val = bt_arr_to_hex(ctx.get_value(self.variable))
        elif self.variable[0] in [token.STR.value, token.INT.value]:
            val = bt_arr_to_hex(str_to_bt_arr2(self.variable))
        for b in val:
            print(b, end="")
        print()


class Call:
    def __init__(self, ctx, func, ret, arg_val):
        self.func = func
        self.ret = ret
        self.args = arg_val  # varnames as ctx.loc[-1] keys
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        func = ctx.get_fun(self.func)
        if func.arg_len != len(self.args):
            raise Exception(f"wrong number of parameters in function: {self.func}")
        ctx.assert_exist(self.ret)
        sf = {}

        # self.loc[-1][name[1]] = var
        # ctx.set_var3(func.ret, ret_var)
        for k, v in zip(func.args, self.args):
            if ctx.check_exist(v):
                var = ctx.get_var(v)
                # ctx.set_var3(k, var)
                sf[k[1]] = var
            elif v[0] == token.INT.value:
                bt_arr = str_to_bt_arr2(v[1])
                var = Var(True, None, len(bt_arr))
                var.data = bt_arr
                # ctx.set_var3(k, var)
                sf[k[1]] = var
            else:
                bt_arr = str_to_bt_arr2(v[1])
                var = Var(False, None, len(bt_arr))
                var.data = bt_arr
                # ctx.set_var3(k, var)
                sf[k[1]] = var
        func.stack_frame = sf
        ctx.loc.append(sf)
        for e in func.block:
            e(ctx)
            if isinstance(e, Return):
                ctx.loc[-2][self.ret[1]].data = ctx.loc[-1][e.variable[1]].data
                break
            if ctx.fun_ret is not None:
                ctx.loc[-2][self.ret[1]].data = ctx.loc[-1][ctx.fun_ret.variable[1]].data
                ctx.fun_ret = None
                break

        ctx.loc.pop()
        func.stack_frame = ctx.loc[-1]



