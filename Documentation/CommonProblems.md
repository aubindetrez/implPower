# List of problems you should keep in mind when contributing:
- Declare and assign a signal on one line: `logic test = ...;`
- Always make sure you have proper integer overflow in your Python verification Code
- If you use a BigEndian ISA use BigEndian Vectors
- When writing a bash for loop `for item in $array`, do not forget about the `$`
- Mixing python function arguments when using positional arguments
- Inscape: if you create a rectangle in a group, when you want to resize the rectangle it scales
  it's borders
- Inscape: Snap does not work
- Inscape: Default text size is 30pt
- Inscape: hard to switch between groups
- Github: When you edit an issue or reference it in a commit it adds an item to the issue (After a
  while it can make it hard to follow discussions). Solution: Make smaller issues, but it can make
  it harder for new commers if the issue are too technical/too specific.
- Documentation in every directory (including Readmes), it is much easier to keep up to date when
  everything is in one directory [Documentation/](Documentation/) (+ the main [README.md](README.md))
- Shell: When doing `find a_directory/ -name "*.sv"` do not forget the `"`
- Python: when using `int("0000100101", 2)` forget about the `, 2` (default is decimal)
- When writing a 'Draft' SV design: Interfaces/signals change all the time and it is hard to keep verification in sync with the design 
- SystemVerilog if you do `logic a; assign a = something[0:31];` there is no error, even if it is
  obviously wrong
- Python: having "Unused function..." warning would be able to catch copy/paste typos
