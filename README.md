# PyMacro

Welcome to *pymacro*, a python library that you can use to have MACROS inside your python functions.
It uses a decorator to find and replace macros inside of comments with valid python code. It can 
be used in the following manner.

```py
from pymacro import macro

@macro
def func_with_macro():
    # DEFINE x 10
    print(x)
```

The DSL inside the comments is turned into valid python code.