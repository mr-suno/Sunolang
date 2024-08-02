import string
from strings import *

DIGITS = "0123456789" # Create a list of digits so we can detect if a character is a digit
LETTERS = string.ascii_letters
MIXED = LETTERS + DIGITS

class Error:
   def __init__(self, begin, end, error_name, details):
      self.start = begin
      self.end = end
      self.error_name = error_name
      self.details = details

   def as_string(self):
      result = f"{self.error_name}: {self.details}\n"
      result += f"File {self.start.name}, line {self.start.line + 1}"
      result += "\n\n" + strings(self.start.text, self.start, self.end)
      return result
   
class IllegalCharacter(Error):
   def __init__(self, start, end, details):
      super().__init__(start, end, "Illegal Character", details)

class InvalidSyntax(Error):
   def __init__(self, start, end, details=""):
      super().__init__(start, end, "Invalid Syntax", details)

class RuntimeError(Error):
   def __init__(self, start, end, details="", context=None):
      super().__init__(start, end, "Runtime Error", details)
      self.context = context

## Runtime Results

class RuntimeResult:
   def __init__(self) -> None:
      self.value = None
      self.error = None

   def register(self, result):
      if result.error:
         self.error = result.error
      return result.value
   
   def success(self, value):
      self.value = value
      return self
   
   def failure(self, error):
      self.error = error
      return self

## Position

class Position:
   def __init__(self, index, line_number, column, name, file_text):
      self.index = index
      self.line = line_number
      self.column = column
      self.name = name
      self.text = file_text

   def advance(self, current_char=None):
      self.index += 1
      self.column += 1

      if current_char == "\n":
         self.line += 1
         self.column = 0

      return self
   
   def copy(self):
      return Position(self.index, self.line, self.column, self.name, self.text)

# TT = Token Type

TT_INT = "TT_INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_EOF = "EOF"
TT_POW = "POW"


# Separate tokens, aside from math these handle stuff like variables

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EQ = "EQ"

KEYWORDS = [
   "save"
]
 
class Token:
   def __init__(self, type_, value=None, start=None, end=None):
      self.type = type_
      self.value = value

      if start:
         self.start = start.copy()
         self.end = start.copy()
         self.end.advance()

      if end:
         self.end = end

   def matches(self, type_, value):
      return self.type == type_ and self.value == value

   def __repr__(self):
      if self.value:
         return f"{self.type}:{self.value}"
      return f"{self.type}"

   def __str__(self):
      return self.__repr__()

## Lexer

class Lexer:
   def __init__(self, name, text):
      self.text = text
      self.name = name
      self.pos = Position(-1, 0, -1, name, text)
      self.current_char = None
      self.advance()

   def advance(self):
      self.pos.advance(self.current_char)
      self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

   def make_tokens(self):
      tokens = []

      while self.current_char != None:
         if self.current_char in " \t":
            self.advance()
         elif self.current_char in DIGITS:
            tokens.append(self.make_number())
         elif self.current_char in LETTERS:
            tokens.append(self.make_identifier())
         elif self.current_char == "+":
            tokens.append(Token(TT_PLUS, start=self.pos))
            self.advance()
         elif self.current_char == "-":
            tokens.append(Token(TT_MINUS, start=self.pos))
            self.advance()
         elif self.current_char == "*":
            tokens.append(Token(TT_MUL, start=self.pos))
            self.advance()
         elif self.current_char == "/":
            tokens.append(Token(TT_DIV, start=self.pos))
            self.advance()
         elif self.current_char == "(":
            tokens.append(Token(TT_LPAREN, start=self.pos))
            self.advance()
         elif self.current_char == ")":
            tokens.append(Token(TT_RPAREN, start=self.pos))
            self.advance()
         elif self.current_char == "^":
            tokens.append(Token(TT_POW, start=self.pos))
            self.advance()
         elif self.current_char == "=":
            tokens.append(Token(TT_EQ, start=self.pos))
            self.advance()
         else:
            start = self.pos.copy()
            char = self.current_char
            self.advance()
            
            return [], IllegalCharacter(start, self.pos, "\"" + char + "\"")

      tokens.append(Token(TT_EOF, start=self.pos))
      return tokens, None
   
   def make_number(self):
      num_str = ""
      dot_count = 0
      start = self.pos.copy()

      while self.current_char != None and self.current_char in DIGITS + ".":
         if self.current_char == ".":
            if dot_count == 1: # Since a number cannot have more than one decimal in them
               break
            
            dot_count += 1
            num_str += "."
         else:
            num_str += self.current_char
         self.advance()

      if dot_count == 0:
         return Token(TT_INT, int(num_str), start, self.pos)
      else:
         return Token(TT_FLOAT, float(num_str), start, self.pos)
   
   def make_identifier(self):
      identifier_str = ""
      start = self.pos.copy()

      while self.current_char != None and self.current_char in MIXED + "_":
         identifier_str += self.current_char
         self.advance()

      token_type = TT_KEYWORD if identifier_str in KEYWORDS else TT_IDENTIFIER
      return Token(token_type, identifier_str, start, self.pos)

class NumberNode:
   def __init__(self, token):
      self.token = token

      self.start = self.token.start
      self.end = self.token.end

   def __repr__(self):
      return f"{self.token.value}"

class VarAccessNode:
   def __init__(self, var_name_token):
      self.var_name_token = var_name_token

      self.start = self.var_name_token.start
      self.end = self.var_name_token.end

class VarAssignNode:
   def __init__(self, var_name_token, value_node):
      self.var_name_token = var_name_token
      self.value_node = value_node

      self.start = self.var_name_token.start
      self.end = self.var_name_token.end

class BinOpNode:
   def __init__(self, left_node, op_token, right_node):
      self.left_node = left_node
      self.op_token = op_token
      self.right_node = right_node

      self.start = self.left_node.start
      self.end = self.right_node.end

   def __repr__(self):
      return f"({self.left_node}, {self.op_token}, {self.right_node})"
   
class UnaryOpNode:
   def __init__(self, op_token, node):
      self.op_token = op_token
      self.node = node

      self.start = self.op_token.start
      self.end = node.end

   def __repr__(self):
      return f"({self.op_token}, {self.node})"

   def __str__(self):
      return self.__repr__()
   
## Parser

class ParseResult:
   def __init__(self):
      self.error = None
      self.node = None

   def register(self, result):
      if result.error:
         self.error = result.error

      return result.node
   
   def success(self, node):
      self.node = node
      return self
   
   def failure(self, error_code):
      self.error = error_code
      return self

class Parser:
   def __init__(self, tokens):
      self.tokens = tokens
      self.token_index = -1
      self.advance()

   def advance(self):
      self.token_index += 1

      if self.token_index < len(self.tokens):
         self.current_token = self.tokens[self.token_index]

      return self.current_token
   
   def parse(self):
      result = self.expression()

      if not result.error and self.current_token.type != TT_EOF:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"+\", \"-\", \"*\", \"/\" or \"^\""))
      
      return result
   
   def atom(self):
      result = ParseResult()
      token = self.current_token

      if token.type in (TT_INT, TT_FLOAT):
         result.register(self.advance())
         return result.success(NumberNode(token))
      elif token.type == TT_IDENTIFIER:
         result.register(self.advance())
         return result.success(VarAccessNode(token))
      elif token.type == TT_LPAREN:
         result.register(self.advance())
         expression = result.register(self.expression())

         if result.error:
            return result
         
         if self.current_token.type == TT_RPAREN:
            result.register(self.advance())
            return result.success(expression)
         else:
            return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, f"Expected \")\", got {self.current_token}"))
         
      return result.failure(InvalidSyntax(token.start, token.end, "Expected Integer, Float, \"+\", \"-\" or \"(\""))

   def power(self):
      return self.binary_operation(self.atom, (TT_POW, ), self.factor)

   def factor(self):
      # Factoring and managing all sorts of operations
      result = ParseResult()
      token = self.current_token

      if token.type in (TT_PLUS, TT_MINUS):
         result.register(self.advance())
         factor = result.register(self.factor())

         if result.error:
            return result
         
         return result.success(UnaryOpNode(token, factor))

      return self.power()
   
   def term(self):
      return self.binary_operation(self.factor, (TT_MUL, TT_DIV))
   
   def expression(self):
      result = ParseResult()

      if self.current_token.matches(TT_KEYWORD, "save"):
         result.register(self.advance())

         if self.current_token.type != TT_IDENTIFIER:
            return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected Identifier"))
         
         var_name = self.current_token
         result.register(self.advance())

         if self.current_token.type != TT_EQ:
            return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"as\""))
         
         result.register(self.advance())
         expression = result.register(self.expression())

         if result.error:
            return result
         
         return result.success(VarAssignNode(var_name, expression))

      return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))
   
   def binary_operation(self, function, ops, alternative=None):
      if alternative == None:
         alternative = function

      result = ParseResult()
      left = result.register(function())

      if result.error:
         return result
      
      while self.current_token.type in ops:
         op_token = self.current_token

         result.register(self.advance())
         right = result.register(alternative())

         if result.error:
            return result
         
         left = BinOpNode(left, op_token, right)

      return result.success(left)

## Values

class Number:
   def __init__(self, value):
      self.value = value
      self.set_pos()
      self.set_context()
   
   def set_pos(self, start=None, end=None):
      self.start = start
      self.end = end

      return self
   
   def set_context(self, context=None):
      self.context = context
      return self
   
   def added_to(self, other):
      if isinstance(other, Number):
         return Number(self.value + other.value).set_context(self.context), None
   
   def subbed_by(self, other):
      if isinstance(other, Number):
         return Number(self.value - other.value).set_context(self.context), None
   
   def mul_by(self, other):
      if isinstance(other, Number):
         return Number(self.value * other.value).set_context(self.context), None
   
   def div_by(self, other):
      if isinstance(other, Number):
         if other.value == 0:
            return None, RuntimeError(other.start, other.end, "Illegal division, cannot divide by 0", self.context)
         return Number(self.value / other.value).set_context(self.context), None
      
   def pow_by(self, other):
      if isinstance(other, Number):
         return Number(self.value ** other.value).set_context(self.context), None
   
   def __repr__(self):
      return str(self.value)

## Context

class Context:
   def __init__(self, display_name, parent=None, parent_entry=None) -> None:
      self.display_name = display_name
      self.parent = parent
      self.parent_entry = parent_entry
      self.symbol_table = None

class SymbolTable:
   def __init__(self) -> None:
      self.symbols = {}
      self.parent = None

   def get(self, name):
      value = self.symbols.get(name, None)

      if value == None and self.parent:
         return self.parent.get(name)
      
      return value
   
   def set(self, name, value):
      self.symbols[name] = value

   def remove(self, name):
      del self.symbols[name]

## Interpreter

class Interpreter:
   def visit(self, node, context):
      method_name = f"visit_{type(node).__name__}"
      method = getattr(self, method_name, self.no_visit_method)

      return method(node, context)

   def no_visit_method(self, node, context):
      raise Exception(f"No visit_{type(node).__name__} method defined")

   def visit_NumberNode(self, node, context):
      return RuntimeResult().success(Number(node.token.value).set_context(context).set_pos(node.start, node.end))

   def visit_VarAccessNode(self, node, context):
      result = RuntimeResult()
      var_name = node.var_name_token.value
      value = context.symbol_table.get(var_name)

      if not value:
         return result.failure(RuntimeError(node.start, node.end, f"\"{var_name}\" undefined", context))
      
      return result.success(value)
   
   def visit_VarAssignNode(self, node, context):
      result = RuntimeResult()
      var_name = node.var_name_token.value
      value = result.register(self.visit(node.value_node, context))

      if result.error:
         return result
      
      context.symbol_table.set(var_name, value)
      return result.success(value)

   def visit_BinOpNode(self, node, context):
      res = RuntimeResult()

      left = res.register(self.visit(node.left_node, context))
      if res.error:
         return res

      right = res.register(self.visit(node.right_node, context))
      if res.error:
         return res

      if node.op_token.type == TT_PLUS:
         result, error_code = left.added_to(right)
      elif node.op_token.type == TT_MINUS:
         result, error_code = left.subbed_by(right)
      elif node.op_token.type == TT_MUL:
         result, error_code = left.mul_by(right)
      elif node.op_token.type == TT_DIV:
         result, error_code = left.div_by(right)
      elif node.op_token.type == TT_POW:
         result, error_code = left.pow_by(right)
      else:
         raise Exception(f"Invalid operator: {node.op_token.type}")
      
      if error_code:
         return res.failure(error_code)
      else:
         return res.success(result.set_pos(node.start, node.end))

   def visit_UnaryOpNode(self, node, context):
      result = RuntimeResult()
      number = self.visit(node.node, context)
      
      if result.error:
         return result

      if node.op_token.type == TT_MINUS:
         number, error_code = number.mul_by(Number(-1))

      if error_code:
         return result.failure(error_code)
      else:
         return result.success(number.set_pos(node.start, node.end))

## Run functions

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))

def run(name, text):
   lexer = Lexer(name, text)
   tokens, error_code = lexer.make_tokens()

   if error_code:
      return None, error_code
   
   parser = Parser(tokens)
   ast = parser.parse()

   if ast.error:
      return None, ast.error
   
   interpreter = Interpreter()
   context = Context("<Program>")
   context.symbol_table = global_symbol_table
   result = interpreter.visit(ast.node, context)

   return result.value, result.error
