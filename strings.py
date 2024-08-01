def strings(text, start, end):
   result = ""

   # Calculate our indices
   index_start = max(text.rfind("\n", 0, start.index), 0)
   index_end = text.find("\n", index_start + 1)

   if index_end < 0:
      index_end = len(text)

   # Generate each line
   line_count = end.line - start.line + 1
   for i in range(line_count):
      line = text[index_start:index_end]

      col_start = start.column if i == 0 else 0
      col_end = end.column if i == line_count - 1 else len(line) - 1

      result += line + "\n"
      result += " " * col_start + "^" * (col_end - col_start)

      # Recalculating everything because fuck you that's why
      index_start = index_end
      index_end = text.find("\n", index_start + 1)

      if index_end < 0:
         index_end = len(text)

   return result.replace("\t", "")