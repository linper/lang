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
