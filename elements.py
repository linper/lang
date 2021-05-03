import random

from utils import *
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


# also a variable object
class Initializer:
    def __init__(self, is_int, name, length=4):
        self.is_int = is_int
        self.name = name
        # strings and ints are saved in same byte array
        self.value = bytearray(length)
        self.length = length

    def __call__(self, context):
        if context.loc[-1].get(self.name) is not None:
            raise Exception(f"variable: {self.name}, already exists")
        context.loc[-1][self.name] = self.value
        # context.elem.append(self)
        context.cur_block.append(self)


class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __call__(self, context):
        if context.loc[-1].get(self.name) is None:
            raise Exception(f"variable: {self.name}, is not declared")
        var = context.loc[-1][self.name]
        if var.is_int():
            # TODO some smart stringified long int to byte array conversion. For now set random
            for i in range(len(var.value)):
                var.value[i] = random.randint(0, 255)
        else:
            if len(self.name) > var.length:
                raise Exception(f"out of bounds for: {self.name}, with: {self.value}")
            for i in range(1, len(self.value) + 1):
                var.value[-i] = ord(self.value[-i])
        # context.elem.append(self)
        context.cur_block.append(self)


class Expression:
    def __init__(self, result, first, second, expr):
        self.result = result
        self.first = first
        self.second = second
        self.expr = expr

    def __call__(self, context):
        if context.loc[-1].get(self.result) is None:
            raise Exception(f"variable: {self.result}, is not declared")
        if context.loc[-1].get(self.first) is None:
            raise Exception(f"variable: {self.first}, is not declared")
        if context.loc[-1].get(self.second) is None:
            raise Exception(f"variable: {self.second}, is not declared")
        result = context.loc[-1][self.result]
        first = context.loc[-1][self.first]
        second = context.loc[-1][self.second]
        int_math[self.expr](result, first, second)
        # context.elem.append(self)
        context.cur_block.append(self)


class If:
    def __init__(self, cond):
        self.cond = cond
        self.elem = []  # TODO

    def __call__(self, context):
        if context.loc[-1].get(self.cond) is None:
            raise Exception(f"variable: {self.cond}, is not declared")
        cond = context.loc[-1][self.cond]
        context.cur_block.append(self)
        context.cur_block = self.elem
        if cond.value != 0:
            for e in self.elem:
                e(self)


class While:
    def __init__(self, cond):
        self.cond = cond
        self.elem = []  # TODO

    def __call__(self, context):
        if context.loc[-1].get(self.cond) is None:
            raise Exception(f"variable: {self.cond}, is not declared")
        cond = context.loc[-1][self.cond]
        context.cur_block.append(self)
        context.cur_block = self.elem
        while cond.value != 0:
            for e in self.elem:
                e(self)


class Func:
    def __init__(self, name, ret, args):
        self.name = name
        self.ret = ret
        self.stack_frame = {}  # varnames as context.loc[-1] keys
        self.args = args  # varnames
        self.arg_len = len(args)
        self.elem = []

    def __call__(self, context):
        for a in self.args:
            self.stack_frame[a] = None
        if context.fun.get(self.name) is not None:
            raise Exception(f"function: {self.name}, already declared")
        context.fun[self.name] = self
        context.cur_block.append(self)
        context.cur_block = self.elem


class Return:
    def __init__(self, variable):
        self.variable = variable

    def __call__(self, context):
        if context.loc[-1].get(self.variable) is None:
            raise Exception(f"variable: {self.variable}, is not declared")


class Call:
    def __init__(self, func, ret, *arg_val):
        self.func = func
        self.ret = ret
        self.args = arg_val  # varnames as context.loc[-1] keys

    def __call__(self, context):
        if context.fun.get(self.func) is None:
            raise Exception(f"function: {self.func}, is not declared")
        func = context.fun[self.func]
        if context.loc[-1].get(self.ret) is None:
            raise Exception(f"variable: {self.ret}, is not declared")
        if len(func.args) != len(self.args):
            raise Exception(f"wrong number of parameters in function: {self.func}")
        for k, v in zip(func.args, self.args):  # setting parameters in stackframe for called function
            func.stack_frame[k] = v
        context.loc.append(func.stack_frame)
        for e in func.elem:
            e(context)
            if not isinstance(e, Return):
                context.loc[-2][self.ret] = context.loc[-1][e.variable]
                break
        context.pop()



