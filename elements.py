import random

from utils import *
from int_math import *
# from lexer import *


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

    def assert_not_exist(self, data):
        if data[0] in [token.VAR.value, token.VNAME.value]:
            if self.loc[-1].get(data[1]) is not None:
                raise Exception(f"variable: {data[1]}, already exists")

    def assert_exist(self, data):
        if data[0] in [token.VAR.value, token.VNAME.value]:
            if self.loc[-1].get(data[1]) is None:
                raise Exception(f"variable: {data[1]}, does not exists")

    def set_var(self, var):
        self.loc[-1][var.name] = var


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
        self.block = []  # TODO
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        if ctx.loc[-1].get(self.cond) is None:
            raise Exception(f"variable: {self.cond}, is not declared")
        cond = ctx.loc[-1][self.cond]
        ctx.cur_block.append(self)
        ctx.cur_block = self.block
        if cond.value != 0:
            for e in self.block:
                e(self)


class While:
    def __init__(self, ctx, cond):
        self.cond = cond
        self.block = []  # TODO
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        if ctx.loc[-1].get(self.cond) is None:
            raise Exception(f"variable: {self.cond}, is not declared")
        cond = ctx.loc[-1][self.cond]
        ctx.cur_block.append(self)
        ctx.cur_block = self.block
        while cond.value != 0:
            for e in self.block:
                e(self)


class Func:
    def __init__(self, ctx, name, args):
        self.name = name
        self.stack_frame = {}  # varnames as ctx.loc[-1] keys
        self.args = args  # varnames
        self.arg_len = len(args)
        self.block = []
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        for a in self.args:
            self.stack_frame[a] = None
        if ctx.fun.get(self.name) is not None:
            raise Exception(f"function: {self.name}, already declared")
        ctx.fun[self.name] = self
        ctx.cur_block.append(self)
        ctx.cur_block = self.block


class Return:
    def __init__(self, ctx, variable):
        self.variable = variable
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        if ctx.loc[-1].get(self.variable) is None:
            raise Exception(f"variable: {self.variable}, is not declared")


class Call:
    def __init__(self, ctx, func, ret, *arg_val):
        self.func = func
        self.ret = ret
        self.args = arg_val  # varnames as ctx.loc[-1] keys
        ctx.cur_block.append(self)

    def __call__(self, ctx):
        if ctx.fun.get(self.func) is None:
            raise Exception(f"function: {self.func}, is not declared")
        func = ctx.fun[self.func]
        if ctx.loc[-1].get(self.ret) is None:
            raise Exception(f"variable: {self.ret}, is not declared")
        if len(func.args) != len(self.args):
            raise Exception(f"wrong number of parameters in function: {self.func}")
        for k, v in zip(func.args, self.args):  # setting parameters in stackframe for called function
            func.stack_frame[k] = v
        ctx.loc.append(func.stack_frame)
        for e in func.elem:
            e(ctx)
            if not isinstance(e, Return):
                ctx.loc[-2][self.ret] = ctx.loc[-1][e.variable]
                break
        ctx.pop()



