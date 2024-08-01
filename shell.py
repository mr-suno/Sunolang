import basic

while True:
   text = input("Basic > ")
   result, error_code = basic.run("\"Yes\"", text)

   if error_code:
      print(error_code.as_string())
   else:
      print(result)