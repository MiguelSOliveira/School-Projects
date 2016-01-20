# -*- coding: utf-8 -*-

# Authors:
#	João Luis Rodrigues Paulo - up201306220
#	José Miguel Santos Oliveira - up201304192

import ply.yacc as yacc
import ply.lex as lex
import sys, os.path, re

tokens = [
    'MAIN',
    'VAR', 'NUMBER', 'BOOLEAN',
    'OR', 'AND', 'NOT',
    'LESSEQUAL', 'GREATEREQUAL', 'LESSTHAN', 'GREATERTHAN', 'EQUALS', 'NOTEQUALS',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK',
    'COMMA', 'SEMICOLON', 'ASSIGN',
]

t_ignore       = ' \t'
t_NUMBER       = r'\d+'
t_OR           = r'\|\|'
t_NOT          = r'!'
t_AND          = r'&&'
t_LPAREN       = r'\('
t_RPAREN       = r'\)'
t_LBRACK       = r'\{'
t_RBRACK       = r'\}'
t_LESSEQUAL    = r'<='
t_GREATEREQUAL = r'>='
t_EQUALS       = r'\=\='
t_GREATERTHAN  = r'>'
t_LESSTHAN     = r'<'
t_NOTEQUALS    = r'!='
t_PLUS         = r'\+'
t_MINUS        = r'-'
t_TIMES        = r'\*'
t_DIVIDE       = r'/'
t_ASSIGN       = r'\='
t_SEMICOLON    = r';'
t_COMMA        = r','

precedence = (
    ('left', 'NOT'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'LESSTHAN', 'GREATERTHAN', 'GREATEREQUAL', 'LESSEQUAL', 'NOTEQUALS', 'EQUALS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

reserved = {
   'int'    : 'INT',
   'bool'   : 'BOOL',
   'void'   : 'VOID',
   'if'     : 'IF',
   'else'   : 'ELSE',
   'while'  : 'WHILE',
   'return' : 'RETURN',
}

tokens += list(reserved.values())

##
# Regex MAIN, BOOLEAN, VAR's & NewLine
##
def t_MAIN(t):
    r'main\(\)\s\{'
    return t

def t_BOOLEAN(t):
    r'(true|false)'
    return t

def t_VAR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[ t.value ]
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

##
# Initiate State of Automaton
##
def p_main(p):
    'main : MAIN init RBRACK'
    p[0] = ('main', p[2])

def p_main_simple(p):
    '''main : VOID MAIN init RBRACK
            | INT MAIN init RBRACK'''
    p[0] = ('main', p[3])

##
# An second initial state to take care of reading n lines of our file, some of states have a transition to this one, so we can parse everything
##
def p_init(p):
    '''init : cond init
            | declare init
            | atrib init
            | loop init
            | return init'''
    if p[2]:
        p[0] = (p[1],) + p[2]
    else:
        p[0] = (p[1],)

##
# IF THEN ELSE Conditions
##
def p_cond_if(p):
    '''cond : IF LPAREN bool_exp RPAREN LBRACK init RBRACK
            | IF LPAREN VAR RPAREN LBRACK init RBRACK
            | IF LPAREN NUMBER RPAREN LBRACK init RBRACK
    '''
    p[0] = ('if', p[3]) + p[6]

def p_cond_if_else(p):
    '''cond : IF LPAREN bool_exp RPAREN LBRACK init RBRACK ELSE LBRACK init RBRACK
            | IF LPAREN VAR RPAREN LBRACK init RBRACK ELSE LBRACK init RBRACK
            | IF LPAREN NUMBER RPAREN LBRACK init RBRACK ELSE LBRACK init RBRACK'''
    p[0] = ('if-else', p[3]) + p[6] + p[10]

def p_loop_while(p):
    '''loop : WHILE LPAREN bool_exp RPAREN LBRACK init RBRACK
            | WHILE LPAREN VAR RPAREN LBRACK init RBRACK
            | WHILE LPAREN NUMBER RPAREN LBRACK init RBRACK'''
    p[0] = ('while', p[3]) + p[6]

##
# Arithmetic Validations
##
def p_statement_op(p):
    '''statement : aritm LESSEQUAL aritm
                 | aritm GREATEREQUAL aritm
                 | aritm LESSTHAN aritm
                 | aritm GREATERTHAN aritm
                 | aritm EQUALS aritm
                 | aritm NOTEQUALS aritm'''
    p[0] = (p[2], p[1], p[3])

def p_statement_atrib_or_bool(p):
    '''statement : atrib
                 | BOOLEAN'''
    p[0] = p[1]

##
# Boolean Expressions
##
def p_bool_exp_and_or(p):
    '''bool_exp : bool_exp AND bool_exp
                | bool_exp OR bool_exp'''
    p[0] = (p[2], p[1], p[3])

def p_bool_exp_paren(p):
    'bool_exp : LPAREN bool_exp RPAREN'
    p[0] = p[2]

def p_bool_exp_not(p):
    'bool_exp : NOT LPAREN statement RPAREN'
    p[0] = (p[1], p[3])

def p_bool_exp_statement(p):
    'bool_exp : statement'
    p[0] = p[1]

##
# Arithmetic expressions
##
def p_aritm(p):
    '''aritm : VAR
             | NUMBER'''
    p[0] = p[1]

def p_aritm_paren(p):
    'aritm : LPAREN aritm RPAREN'
    p[0] = p[2]

def p_aritm_op(p):
    '''aritm : aritm PLUS aritm
             | aritm MINUS aritm
             | aritm TIMES aritm
             | aritm DIVIDE aritm'''
    p[0] = (p[2], p[1], p[3])

##
# Variable Assignments
##
def p_atrib_numbers(p):
    '''atrib : VAR ASSIGN aritm SEMICOLON
             | VAR ASSIGN aritm RPAREN'''
    p[0] = (p[2], p[1], p[3])

def p_atrib_bools(p):
    '''atrib : VAR ASSIGN bool_exp SEMICOLON
             | VAR ASSIGN bool_exp RPAREN'''
    p[0] = (p[2], p[1], p[3])

##
# Declarations
##
def p_declare(p):
    '''declare : INT VAR ASSIGN aritm SEMICOLON
               | BOOL VAR ASSIGN bool_exp SEMICOLON'''
    p[0] = (p[1], (p[3], p[2], p[4]))

def p_declare_complex(p):
    '''declare : INT VAR ASSIGN aritm COMMA declare_same_line
               | BOOL VAR ASSIGN bool_exp COMMA declare_same_line'''
    p[0] = (p[1],) + ((p[3], p[2], p[4]),) + p[6]

def p_declare_simple(p):
    '''declare : INT VAR SEMICOLON
               | BOOL VAR SEMICOLON
               | INT VAR COMMA declare_same_line
               | BOOL VAR COMMA declare_same_line'''
    if len(p) == 5:
        p[0] = (p[1], p[2]) + p[4]
    else:
        p[0] = (p[1], p[2])

def p_declare_same_line(p):
    '''declare_same_line : VAR COMMA declare_same_line
                         | VAR SEMICOLON
                         | VAR ASSIGN aritm COMMA declare_same_line
                         | VAR ASSIGN aritm SEMICOLON
                         | VAR ASSIGN bool_exp COMMA declare_same_line
                         | VAR ASSIGN bool_exp SEMICOLON'''
    if len(p) == 6:
        p[0] = ((p[2], p[1], p[3]),) + p[5]
    elif len(p) == 5:
        p[0] = ((p[2], p[1],p[3]),)
    elif len(p) == 4:
        p[0] = (p[1],) + p[3]
    else:
        p[0] = (p[1],)

def p_return(p):
    '''return : RETURN aritm SEMICOLON
              | RETURN BOOLEAN SEMICOLON'''
    p[0] = (p[1],) + (p[2],)

##
# State where Automaton ends, there is nothing to parse anymore
##
def p_init_empty(p):
    'init : empty'

def p_empty(p):
    'empty : '
    pass

##
# Processing Errors
##
def p_error(p):
  print("Syntax error in program given.")

def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)

##
# 3 Registers Code Generation
##

labels = []
def new_label():
  if len(labels) > 0:
    idx = int(labels[-1].split("L")[1]) + 1
    labels.append("L" + str(idx))
  else:
    labels.append("L1")

  return labels[-1]

def compile_exp(exp):
  lista = compile_expREC(exp, -1)
  arg = lista.split()[0]

  tmp = exp[1]
  return (arg, tmp, lista)

def compile_expREC(exp, t):
  if not isinstance(exp, tuple): return str(exp)

  t += 1
  signal = exp[0]

  if signal == "=" and len(exp) > 2 and isinstance(exp[2], tuple):
    return compile_expREC(exp[2], t-1)
  elif signal == "=":
  	return "t" + str(t) + " = " + compile_expREC(exp[2], t)
  elif isinstance(exp[2], tuple) and isinstance(exp[1], tuple):
    return "t" + str(t) + " = " + 't' + str(t+1) + signal + 't' + str(t+2) + ', ' + compile_expREC(exp[1], t) + ', ' + compile_expREC(exp[2], t+1)
  elif isinstance(exp[2], tuple):
    return "t" + str(t) + " = " + compile_expREC(exp[1], t) + signal + 't' + str(t+1) + ', ' + compile_expREC(exp[2], t)
  elif isinstance(exp[1], tuple):
    return 't' + str(t) + ' = ' + 't' + str(t+1) + signal + compile_expREC(exp[2], t) + ', ' + compile_expREC(exp[1], t)
  else:
    return "t" + str(t) + " = " + compile_expREC(exp[1], t) + signal + compile_expREC(exp[2], t)

def return_compile(cmd):
  if isinstance(cmd[1:][0], tuple):
    tempValue = compile_exp(cmd[1:][0])
    # Define return variable as RET
    tList = list(tempValue)
    temp = tList.pop(1)
    tList.insert(1, "_ret")
    tempValue = tuple(tList)
  else: tempValue = cmd[1:][0]

  return list(("return", tempValue))

def compile_cmd(cmd):
  if cmd[0] == "if" or cmd[0] == "if-else":
    return if_compile(cmd)
  elif cmd[0] == "while":
    return while_compile(cmd)
  elif cmd[0] == "return":
    return return_compile(cmd)
  elif cmd[0] == '=':
    return compile_exp(cmd)
  else:
    lista = []
    if cmd[0] in types:
      for elem in cmd[1:]:
        if isinstance(elem, tuple):
          lista.append(compile_cmd(elem))
    else:
      if isinstance(cmd[0], tuple):
        for elem in cmd:
          lista.append(compile_cmd(elem))
    return lista


# L1: new_label()
# (if, E, C, C2) -> (lista, (if_false, main_arg, L1), code1, (GOTO, FINAL), (label, L1), code2, (label, FINAL))
def if_compile(exp):
  # Expressao para 3 Registos
  first_arg = exp[1]
  (main_arg,tmp,lista) = compile_exp(first_arg)

  if len(exp[2:]) == 1:
    tmp = exp[2]
  else: tmp = exp[2:]

  if exp[0] == "if-else":
    label = new_label()
  labelFinal = new_label()

  if exp[0] == "if":
    return list((lista, ("if_false", main_arg, labelFinal), compile_cmd(tmp), ("label", labelFinal)))
  else:
    return list((lista, ("if_false", main_arg, label), compile_cmd(tmp), ("GOTO", labelFinal), ("label", label), compile_cmd(exp[3]), ("label", labelFinal)))


# (while, E, C) -> (('label', 'L1'), l, ('if_false', v, 'L2'), l2, ('goto', 'L1'), ('label', 'L2'))
# (v,l) = compile_exp(e)
# l2 = compile_cmd(c)
def while_compile(exp):
  first_arg = exp[1]
  (main_arg,tmp, lista) = compile_exp(first_arg)

  if len(exp[2:]) == 1:
    tmp = exp[2]
  else: tmp = exp[2:]

  label = new_label()
  labelFinal = new_label()
  return list((("label", label), lista, ("if_false", main_arg, labelFinal), compile_cmd(tmp), ("GOTO", label), ("label", labelFinal)))

##
# Tokenizing && Parsing
##
lexer = lex.lex()
parser = yacc.yacc()

##
# Input from user
##
if os.path.isfile(sys.argv[1]):
  data = open(sys.argv[1]).read()
else:
  print("Re-run the parser with a valid filename")
  exit(1)

##
# Recursive Compiling of code to 3 registers
##
compiled3Reg = []
def recursiveCompile(data):
  global compiled3Reg
  for elem in data[1]:
    compiled3Reg.append(compile_cmd(elem))
  compiled3Reg = [x for x in compiled3Reg if x != []]

symbolicTable = []
types = ['int', 'bool']
BoolValues = ['false', 'true']
def addSymbol(data):
  for elem in data:
    if isinstance(elem, tuple):
      symbolicTable.append(elem[1])
    else:
      symbolicTable.append(elem)

def recursiveSimbolTable(data):
  if not isinstance(data, tuple): return
  for elem in data:
    if elem[0] in types:
      addSymbol(elem[1:])
    recursiveSimbolTable(elem)

##
# MIPS Printing
##
def reverseOrder(elem):
	return elem[::-1]

bools = {'false': '0', 'true': '1'}
opers = {'+': 'add', '-': 'sub', '*': 'mul', '/': 'div'}
registers = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9"]
def parseAritm(elem, offset):
	global finalTree
	elemS = elem.split(' = ')
	oper = None
	
	if len(elem) == 1: return

	if elemS[1] in bools:
		elemS[1] = bools[elemS[1]]

	for elemSU in elemS[1]:
		if elemSU in opers:
			elemSUR = elemS[1].split(elemSU)
			oper = opers[elemSU]

	if oper:
		for idx in range(len(elemSUR)):
			if elemSUR[idx] in symbolicTable:
				finalTree += "\tlw $t" + str(offset) + ", " + elemSUR[idx] + "\n"
				elemSUR[idx] = "t" + str(offset)
				offset += 1

		if oper == 'sub' or oper == 'add':
			if elemSUR[0] in registers and elemSUR[1] in registers:
				finalTree += "\t" + oper + " $" + elemS[0] + ", $" + elemSUR[0] + ", $" + elemSUR[1] + '\n'
			elif elemSUR[0] in registers:
				finalTree += "\t" + oper + "i $" + elemS[0] + ", $" + elemSUR[0] + ", " + elemSUR[1] + '\n'
			elif elemSUR[1] in registers:
				finalTree += "\t" + oper + "i $" + elemS[0] + ", $" + elemSUR[1] + ", " + elemSUR[0] + '\n'
			else:
				finalTree += "\tli $t" + str(int(elemS[0][1:])+offset) + ", " + elemSUR[0] + '\n'
				finalTree += "\t" + oper + "i $" + elemS[0] + ", $t" + str(int(elemS[0][1:])+offset) + ", " + elemSUR[1] + '\n'
		else:
			if elemSUR[0] in registers and elemSUR[1]in registers:
				finalTree += "\t" + oper + " $" + elemS[0] + ", $" + elemSUR[0] + ", $" + elemSUR[1] + '\n'
			elif elemSUR[0] in registers:
				finalTree += "\t" + oper + " $" + elemS[0] + ", $" + elemSUR[0] + ", " + elemSUR[1] + '\n'
			elif elemSUR[1] in registers:
				finalTree += "\t" + oper + " $" + elemS[0] + ", $" + elemSUR[1] + ", " + elemSUR[0] + '\n'
			else:
				finalTree += "\tli $t" + str(int(elemS[0][1:])+offset) + ", " + elemSUR[0] + '\n'
				finalTree += "\t" + oper + " $" + elemS[0] + ", $t" + str(int(elemS[0][1:])+offset) + ", " + elemSUR[1] + '\n'
	else: finalTree += '\tli $' + elemS[0] + ', ' + elemS[1] + '\n'

def storeData(elem0, elem1):
	global finalTree
	if not elem1 == "_":
		finalTree += '\tsw $' + elem0 + ', ' + elem1 + '\n'

opersIfFalse = {"<":"bgt", ">":"blt", "<=":"bge", ">=":"ble", "==":"bne", "!=":"beq"}
def generateIfFalse(elemS, tmp):
	global finalTree
	if elemS[1] == "true":
		finalTree += "\tbne $t" + str(tmp-1) + ', ' + bools[elemS[1]] + ', ' + elemS[2] + '\n'
	elif elemS[1] == "false":
		finalTree += "\tbeq $t" + str(tmp-1) + ', ' + bools[elemS[1]] + ', ' + elemS[2] + '\n'

def parseMulti(elem):
	global finalTree
	tmp = 0
	cnt = 0
	cntAux = 0
	operation = None
	offset = 0
	# This solve the case when we declare something in main like d = 1+2;
	if isinstance(elem, tuple):
		parseSingle(elem)
	else:
		for elemS in elem:
			if isinstance(elemS, tuple) and "t" in elemS[0]:
				parseSingle(elemS)
			else:
				if str(elemS) in bools:
					finalTree += "\tli $t" + str(tmp) + ', ' + bools[str(elemS)] + '\n'
					tmp+=1
				elif isinstance(elemS, str) and not "r" in elem[0]:
					elemSU = elemS.split(', ')
					elemSU = reverseOrder(elemSU)

					for elemSUR in elemSU:
						elemSUR = elemSUR.split(' = ')
						base = elemSUR
						if len(elemSUR) > 1:
							for s in elemSUR[1]:
								if s in opers:
									temp = elemSUR[1]
									elemSUR.remove(temp)
									elemSUR.insert(1, "_")
									elemSUR.insert(2, elemSUR[0] + ' = ' + temp)
									parseSingle(tuple(elemSUR))

					# This take care of conditions inside of if and while blocks
					for oper in opersIfFalse:
						if len(base) > 1:
							if oper in base[1]:
								if "=" in base[1].split(oper)[1]:
									break
								operation = opersIfFalse[oper]
								baseOffset = base[1].split(oper)
					
					if len(base) > 1:
						for idx in range(len(baseOffset)):
							if baseOffset[idx] in symbolicTable:
								finalTree += "\tlw $t" + str(int(base[0][1]) + offset) + ', ' + baseOffset[idx] + '\n'
								baseOffset[idx] = "t" + str(int(base[0][1]) + offset)
								offset += 1
							elif baseOffset[idx] not in registers:
								finalTree += "\tli $t" + str(int(base[0][1]) + offset) + ', ' + baseOffset[idx] + '\n'
								baseOffset[idx] = "t" + str(int(base[0][1]) + offset)
								offset += 1

					# This Reads the label that will be taken, so we can define IF expression in the right way!
					for elemS1 in elem:
						if isinstance(elemS1, tuple) and "t" in elemS1[0]:
							pass
						else:
							if isinstance(elemS1, tuple):
								if elemS1[0] == 'if_false':
									if cnt == cntAux:
										labelAux = elemS1[2]
									cntAux += 1

					# Branchs
					if len(base) > 1:
						finalTree += "\t" + operation + ' $' + baseOffset[0] + ', $' + baseOffset[1] + ', ' + labelAux + '\n'

				# Reads header from tuple and point where to go next:
				elif isinstance(elemS, tuple):
					if elemS[0] == 'if_false':
						cnt += 1
						generateIfFalse(elemS, tmp)
					elif elemS[0] == 'GOTO':
						finalTree += '\tj ' + elemS[1]
					elif elemS[0] == 'label':
						finalTree += '\n' + elemS[1] + ':'
				else:
					if isinstance(elemS, list):
						for elemSU in elemS:
							if not "t" in elemSU[0]:
								parseSingle(elemSU[0])
							else: parseSingle(elemSU)

def parseSingle(elem):
	elemS = elem[2].split(', ')
	elemS = reverseOrder(elemS)

	offSet = 1

	for elemSU in elemS:
		parseAritm(elemSU, offSet)
		offSet += 1

	storeData(elem[0], elem[1])



##
# Store Data && Print It
##
tree = parser.parse(data)
recursiveSimbolTable(tree[1])
recursiveCompile(tree)

print "Program Tree"
print tree

print "\nSymbolic Table"
print symbolicTable

print "\n3 Registers Tree"
print compiled3Reg

##
# Generate Assembly
##
finalTree = ".data:\n"

for elem in symbolicTable:
	finalTree += '\t' + elem + ': .word\n'

finalTree += '\t_ret: .word\n\n.text:\nmain:\n'

for elem in compiled3Reg:
	if len(elem) > 1:
		parseMulti(elem)
	else:
		parseSingle(elem[0])

print "\nCompiled to: " + sys.argv[1].split('.')[0] + ".asm"
output = open(sys.argv[1].split('.')[0] + ".asm", "w")
output.write(finalTree)
output.close
