from utils import *
from elements import *
import re

tok_array = []
counter = 0

# should be ordered as 'token' enum from utils.py
matchers = [
    re.compile(r"(^(if))"),
    re.compile(r"(^(while))"),
    re.compile(r"(^(func))"),
    re.compile(r"(^(expr))"),
    re.compile(r"(^(call))"),
    re.compile(r"(^(return))[ |;|$]"),
    re.compile(r"(^(new) )"),
    re.compile(r"(^(;))"),
    re.compile(r"(^(string) )"),
    re.compile(r"(^(int) )"),
    re.compile(r"(^(0|[1-9][0-9]*))[\]; ]"),
    re.compile(r'("([A-Za-z0-9_ ]*)")'),
    re.compile(r"(^([a-z_][a-z_A-Z0-9]*))[\]; ]"),
    re.compile(r"(^([A-Z][a-z_A-Z0-9]*))[\]; ]"),
    re.compile(r"^([$]([a-z_A-Z0-9]*))[\]; ]"),
    re.compile(r"(^([+-/*~%]) )"),
    re.compile(r"(^(\[))"),
    re.compile(r"(^(]))"),
    re.compile(r"(^({))"),
    re.compile(r"(^(}))"),
    re.compile(r"^(())$"),
]


# checks if number of curly braces are equal(block is compleated)
def get_cp_balance():
    global counter, tok_array
    counter = 0
    for i, _ in tok_array:
        if i == token.OCBR:
            counter += 1
        if i == token.CCBR:
            counter -= 1
    return counter    


# should be called for every imput line
def get_tok(data):
    global counter, tok_array
    if counter != 0:
        tok_array = []
    while len(data) > 0:
        found = False
        data = data.strip()
        for i, m in enumerate(matchers):
            if m := re.match(m, data):
                tok_array.append((i, m.group(2)))
                print(str(i) + " " + m.group(2))
                data = data[len(m.group(1)):].strip()
                found = True
                break
        if not found:
            raise Exception("syntax error!")
            break
    if counter < 0:
        raise Exception("to much '}'")
    # if block is not finished returns None, and stores incomplete sequence in global scope
    elif counter != 0: 
        return None
    # else returns token-value list
    return tok_array
                

# testing
if __name__ == "__main__":
    with open("source") as f:
        lines = f.readlines()

    for line in lines:
        get_tok(line)
