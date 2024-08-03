import string

def strings(text, start, end):
   result = ""

   # Calculate our indices
   index_start = max(text.rfind("\n", 0, start.index) + 1, 0)
   index_end = text.find("\n", index_start)

   if index_end < 0:
      index_end = len(text)

   # Generate each line
   line_count = end.line - start.line + 1
   for i in range(line_count):
      line = text[index_start:index_end]

      col_start = start.column if i == 0 else 0
      col_end = end.column if i == line_count - 1 else len(line) - 1

      result += line + "\n"
      result += " " * col_start + "^" * (col_end - col_start) + "\n"

      # Recalculating everything
      index_start = index_end + 1
      index_end = text.find("\n", index_start)

      if index_end < 0:
         index_end = len(text)

   return result

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
      return result
   
class ExpectedCharacter(Error):
   def __init__(self, start, end, details):
      super().__init__(start, end, "Expected Character", details)

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
TT_BELOW = "BELOW"
TT_ABOVE = "ABOVE"
TT_AT_MOST = "AT_MOST"
TT_AT_LEAST = "AT_LEAST"
TT_EE = "EE"
TT_NE = "NE"
TT_STRING = "STRING"
TT_CONCAT = "CONCAT"
TT_COMMA = "COMMA"


# Separate tokens, aside from math these handle stuff like variables

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_EQ = "EQ"

KEYWORDS = [
   "save",
   "as",
   "below",
   "above",
   "at_most",
   "at_least",
   "print"
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

      while self.current_char is not None:
         if self.current_char == "/":
            self.skip_comment()
         elif self.current_char in " \t":
            self.advance()
         elif self.current_char in DIGITS:
            tokens.append(self.make_number())
         elif self.current_char in LETTERS:
            tokens.append(self.make_identifier())
         elif self.current_char in ['"', "'"]:
            tokens.append(self.make_string())
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
         elif self.current_char == "\n":
            # Handle newlines here if necessary
            self.advance()  # Skip over the newline
         elif self.current_char == ".":
            start = self.pos.copy()
            self.advance()
            if self.current_char == ".":
               self.advance()
               tokens.append(Token(TT_CONCAT, start=start, end=self.pos))
         elif self.current_char == ",":
            tokens.append(Token(TT_COMMA, start=self.pos))
            self.advance()
         else:
            start = self.pos.copy()
            char = self.current_char
            self.advance()
            return [], IllegalCharacter(start, self.pos, "\"" + char + "\"")

      tokens.append(Token(TT_EOF, start=self.pos))
      return tokens, None

   def peek(self):
      peek = self.pos.index + 1
      return self.text[peek] if peek < len(self.text) else None

   def skip_comment(self):
      if self.current_char == "/":
         if self.peek() == "/":
            self.skip_single_comment()
         elif self.peek() == "*":
            self.skip_multiline_comment()

   def skip_single_comment(self):
      self.advance()
      while self.current_char is not None and self.current_char != "\n":
         self.advance()

   def skip_multiline_comment(self):
      self.advance()
      while self.current_char is not None:
         if self.current_char == "*" and self.peek() == "/":
            self.advance()
            self.advance()
            return
         self.advance()

   def make_string(self):
      string = ""
      start_pos = self.pos.copy()
      escape_character = False
      quote_type = self.current_char

      self.advance()

      escape_characters = {
         'n': '\n',
         't': '\t'
      }

      while self.current_char is not None and (self.current_char != quote_type or escape_character):
         if escape_character:
            string += escape_characters.get(self.current_char, self.current_char)
            escape_character = False
         else:
            if self.current_char == '\\':
               escape_character = True
            else:
               string += self.current_char
         self.advance()

      if self.current_char == quote_type:
         self.advance()
         return Token(TT_STRING, string, start_pos, self.pos)
      
      return None, ExpectedCharacter(start_pos, self.pos, f"Expected closing {quote_type}")

   def make_number(self):
      num_str = ""
      dot_count = 0
      start = self.pos.copy()

      while self.current_char is not None and self.current_char in DIGITS + ".":
         if self.current_char == ".":
            if dot_count == 1:  # Since a number cannot have more than one decimal point
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

      while self.current_char is not None and self.current_char in MIXED + "_":
         identifier_str += self.current_char
         self.advance()

      token_type = TT_KEYWORD if identifier_str in KEYWORDS else TT_IDENTIFIER
      return Token(token_type, identifier_str, start, self.pos)

   def make_below(self):
      token_type = TT_BELOW
      start = self.pos.copy()
      self.advance()

      if self.current_char == "=":
         self.advance()
         token_type = TT_AT_MOST

      return Token(token_type, start=start, end=self.pos)

   def make_above(self):
      token_type = TT_ABOVE
      start = self.pos.copy()
      self.advance()

      if self.current_char == "=":
         self.advance()
         token_type = TT_AT_LEAST

      return Token(token_type, start=start, end=self.pos)

class StringNode:
   def __init__(self, token):
      self.token = token
      self.start = self.token.start
      self.end = self.token.end

   def __repr__(self):
      return f'"{self.token.value}"'

class ListNode:
   def __init__(self, element_nodes):
      self.element_nodes = element_nodes
      self.start = self.element_nodes[0].start if self.element_nodes else None
      self.end = self.element_nodes[-1].end if self.element_nodes else None

class PrintNode:
   def __init__(self, args):
      self.args = args
      self.start = self.args[0].start if self.args else None
      self.end = self.args[-1].end if self.args else None

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
      self.end = self.value_node.end

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
      self.advance_count = 0

   def register_advancement(self):
      self.advance_count += 1

   def register(self, result):
      self.advance_count += result.advance_count
      if isinstance(result, ParseResult):
         if result.error:
            self.error = result.error
         return result.node
      return result
   
   def register_all(self, results):
      for result in results:
         if isinstance(result, ParseResult):
            if result.error:
               self.error = result.error
            self.advance_count += result.advance_count
         self.advance_count += 1
      return self
   
   def success(self, node):
      self.node = node
      return self
   
   def failure(self, error_code):
      if not self.error or self.advance_count == 0:
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
      result = ParseResult()
      statements = []

      while self.current_token.type != TT_EOF:
         statement = result.register(self.statement())

         if result.error:
            return result
         
         statements.append(statement) # Add our statement to our statements array
   
      return result.success(ListNode(statements))

   def var_assign(self):
      result = ParseResult()

      if not self.current_token.matches(TT_KEYWORD, "save"):
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"save\""))
      
      # Advance to the next token
      result.register_advancement()
      self.advance()

      if self.current_token.type != TT_IDENTIFIER:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected identifier"))
      
      var_name = self.current_token
      result.register_advancement()
      self.advance()

      if not self.current_token.matches(TT_KEYWORD, "as"):
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Missing keyword \"as\""))

      result.register_advancement()
      self.advance()

      expression = result.register(self.expression())

      if result.error:
         return result
      
      return result.success(VarAssignNode(var_name, expression))

   def statement(self):
      result = ParseResult()
      
      if self.current_token.matches(TT_KEYWORD, 'print'):
         return self.print_expression()
      
      if self.current_token.matches(TT_KEYWORD, 'save'):
         return self.var_assign()
      
      expr = result.register(self.expression())
      
      if result.error:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"print\", \"save\", int, float, identifier, \"+\", \"-\", \"(\""))
      
      return result.success(expr)
   
   def atom(self):
      result = ParseResult()
      token = self.current_token

      if token.type in (TT_INT, TT_FLOAT):
         result.register_advancement()
         self.advance()
         return result.success(NumberNode(token))
      elif token.type == TT_IDENTIFIER:
         result.register_advancement()
         self.advance()
         return result.success(VarAccessNode(token))
      elif token.type == TT_STRING:
         result.register_advancement()
         self.advance()
         return result.success(StringNode(token))
      elif token.type == TT_LPAREN:
         result.register_advancement()
         self.advance()
         expression = result.register(self.expression())

         if result.error:
            return result
         
         if self.current_token.type == TT_RPAREN:
            result.register_advancement()
            self.advance()
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
         result.register_advancement()
         self.advance()
         factor = result.register(self.factor())

         if result.error:
            return result
         
         return result.success(UnaryOpNode(token, factor))

      return self.power()
   
   def term(self):
      return self.binary_operation(self.factor, (TT_MUL, TT_DIV, TT_CONCAT))
   
   def expression(self):
      result = ParseResult()

      if self.current_token.matches(TT_KEYWORD, "print"):
         print_expression = result.register(self.print_expression())
         
         if result.error:
            return result
         
         return result.success(print_expression)

      if self.current_token.matches(TT_KEYWORD, "save"):
         result.register_advancement()
         self.advance()

         if self.current_token.type != TT_IDENTIFIER:
            return result.failure(InvalidSyntax(
               self.current_token.start, self.current_token.end,
               "Expected identifier"
            ))

         var_name = self.current_token
         result.register_advancement()
         self.advance()

         if self.current_token.type != TT_KEYWORD or self.current_token.value != "as":
            return result.failure(InvalidSyntax(
               self.current_token.start, self.current_token.end,
               "Expected \"as\""
            ))

         result.register_advancement()
         self.advance()

         expr = result.register(self.expression())

         if result.error:
            return result
         
         return result.success(VarAssignNode(var_name, expr))

      node = result.register(self.binary_operation(self.comp_expression, ((TT_KEYWORD, "and"), (TT_KEYWORD, "or"))))

      if result.error:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"save\", int, float, identifier, \"+\", \"-\", \"(\", \"not\", or a comparison operator"))

      return result.success(node)

   def comp_expression(self):
      result = ParseResult()

      if self.current_token.matches(TT_KEYWORD, "not"):
         op_token = self.current_token
         result.register_advancement()
         self.advance()

         node = result.register(self.comp_expression())

         if result.error:
            return result
         
         return result.success(UnaryOpNode(op_token, node))
      
      node = result.register(self.binary_operation(self.arith_expression, (TT_EE, TT_NE, TT_BELOW, TT_ABOVE, TT_AT_MOST, TT_AT_LEAST)))
      
      if result.error:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end,"Expected int, float, identifier, \"+\", \"-\", \"(\", \"not\", or a comparison operator"))

      return result.success(node)

   def arith_expression(self):
      return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))
   
   def binary_operation(self, function, ops, alternative=None):
      if alternative == None:
         alternative = function

      result = ParseResult()
      left = result.register(function())

      if result.error:
         return result
      
      while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
         op_token = self.current_token
         result.register_advancement()
         self.advance()
         right = result.register(alternative())

         if result.error:
            return result
         
         left = BinOpNode(left, op_token, right)

      return result.success(left)
   
   def print_expression(self, expression=None):
      result = ParseResult()

      if not self.current_token.matches(TT_KEYWORD, "print"):
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"print\""))
      
      result.register_advancement()
      self.advance()

      if self.current_token.type != TT_LPAREN:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \"(\" after \"print\""))
      
      result.register_advancement()
      self.advance()

      args = []
      if self.current_token.type != TT_RPAREN:
         args.append(result.register(self.expression()))

         if result.error:
            return result
         
         while self.current_token.type == TT_COMMA:
            result.register_advancement()
            self.advance()

            args.append(result.register(self.expression()))

            if result.error:
               return result
      
      if self.current_token.type != TT_RPAREN:
         return result.failure(InvalidSyntax(self.current_token.start, self.current_token.end, "Expected \")\" after expression in \"print\""))
      
      result.register_advancement()
      self.advance()

      return result.success(PrintNode(args))

## Create a class explicity to handle strings

class String:
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
      if isinstance(other, String):
         return String(self.value + other.value).set_context(self.context), None
      elif isinstance(other, Number):
         return String(self.value + str(other.value)).set_context(self.context), None
      else:
         return None, RuntimeError(other.start, other.end, "Unsupported operand type for string concatenation", self.context)
   
   def concat_with(self, other):
      if isinstance(other, String):
         return String(self.value + other.value).set_context(self.context), None
      elif isinstance(other, Number):
         return String(self.value + str(other.value)).set_context(self.context), None
      else:
         return None, RuntimeError(other.start, other.end, "Unsupported operand type for string concatenation", self.context)
      
   def mul_by(self, other):
      if isinstance(other, Number):
         return String(self.value * int(other.value)).set_context(self.context), None
      else:
         return None, RuntimeError(other.start, other.end, "Unsupported operand type for string multiplication", self.context)
   
   def is_true(self):
      return len(self.value) > 0

   def __repr__(self):
      return f'"{self.value}"'
   
   def __str__(self):
      return self.value

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
   
   def get_comparison_eq(self, other):
      if isinstance(other, Number):
         return Number(int(self.value == other.value)).set_context(self.context), None

   def get_comparison_ne(self, other):
      if isinstance(other, Number):
         return Number(int(self.value != other.value)).set_context(self.context), None

   def get_comparison_lt(self, other):
      if isinstance(other, Number):
         return Number(int(self.value < other.value)).set_context(self.context), None

   def get_comparison_gt(self, other):
      if isinstance(other, Number):
         return Number(int(self.value > other.value)).set_context(self.context), None

   def get_comparison_lte(self, other):
      if isinstance(other, Number):
         return Number(int(self.value <= other.value)).set_context(self.context), None

   def get_comparison_gte(self, other):
      if isinstance(other, Number):
         return Number(int(self.value >= other.value)).set_context(self.context), None

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

   def visit_ListNode(self, node, context):
      result = RuntimeResult()

      for element in node.element_nodes:
         result.register(self.visit(element, context))

         if result.error:
            return result
         
      return result.success(None)

   def visit_StringNode(self, node, context):
      return RuntimeResult().success(String(node.token.value).set_context(context).set_pos(node.start, node.end))

   def visit_PrintNode(self, node, context):
      result = RuntimeResult()
      values = [] # Handles multiple strings easy for concatenation

      for arg in node.args:
         value = result.register(self.visit(arg, context))

         if result.error:
            return result
         
         values.append(value)

      print_str = " ".join(str(value.value) for value in values)
      print(print_str)

      return result.success(Number(0))

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
      elif node.op_token.type == TT_MUL and isinstance(left, String):
         result, error_code = left.mul_by(right)
      elif node.op_token.type == TT_MUL and isinstance(right, String):
         result, error_code = right.mul_by(left)
      elif isinstance(left, Number) and isinstance(right, Number):
         if node.op_token.type == TT_MINUS:
            result, error_code = left.subbed_by(right)
         elif node.op_token.type == TT_MUL:
            result, error_code = left.mul_by(right)
         elif node.op_token.type == TT_DIV:
            result, error_code = left.div_by(right)
         elif node.op_token.type == TT_POW:
            result, error_code = left.pow_by(right)
         elif node.op_token.type == TT_EE:
            result, error_code = left.get_comparison_eq(right)
         elif node.op_token.type == TT_NE:
            result, error_code = left.get_comparison_ne(right)
         elif node.op_token.type == TT_BELOW:
            result, error_code = left.get_comparison_lt(right)
         elif node.op_token.type == TT_ABOVE:
            result, error_code = left.get_comparison_gt(right)
         elif node.op_token.type == TT_AT_MOST:
            result, error_code = left.get_comparison_lte(right)
         elif node.op_token.type == TT_AT_LEAST:
            result, error_code = left.get_comparison_gte(right)
         else:
            return res.failure(RuntimeError(node.start, node.end, f"Invalid operator: {node.op_token.type}", context))
      else:
         return res.failure(RuntimeError(node.start, node.end, "Unsupported operand types for this operation", context))
      
      if error_code:
         return res.failure(error_code)
      else:
         return res.success(result.set_pos(node.start, node.end))

   def visit_UnaryOpNode(self, node, context):
      result = RuntimeResult()
      number = result.register(self.visit(node.node, context))
      
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
   tokens, error = lexer.make_tokens()
   
   if error:
      return None, error
   
   parser = Parser(tokens)
   ast = parser.parse()
   
   if ast.error:
      return None, ast.error
   
   interpreter = Interpreter()
   context = Context("<Program>")
   context.symbol_table = global_symbol_table
   result = interpreter.visit(ast.node, context)
   
   return result.value, result.error