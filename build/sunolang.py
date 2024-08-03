import sys
import basic

if __name__ == "__main__":
   if len(sys.argv) != 2:
      print("Usage: su <filename>")
      sys.exit(1)

   filename = sys.argv[1].strip()

   if not filename.endswith(".su"):
      filename += ".su"

   try:
      with open(filename, 'r') as file:
         content = file.read()
      
      lexer = basic.Lexer(filename, content)
      tokens, error = lexer.make_tokens()
      
      if error:
         print(error.as_string())
      else:
         parser = basic.Parser(tokens)
         ast = parser.parse()
         
         if ast.error:
            print(ast.error.as_string())
         else:
            interpreter = basic.Interpreter()
            context = basic.Context("<Program>")
            context.symbol_table = basic.global_symbol_table
            result = interpreter.visit(ast.node, context)
            
            if result.error:
               print(result.error.as_string())

   except FileNotFoundError:
      print(f"Error: File '{filename}' not found.")
   except Exception as e:
      print(f"Failed to interpret, error code: {e}")