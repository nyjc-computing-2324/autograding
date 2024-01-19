# autograding
Utilities for autograding with unittest

# Usage

```python
import unittest

import autograding
from autograding import case


class TestMyMain(autograding.TestInputOutput):
    def setUp(self):
        self.testcases = [
            case.InOut(input="42", output="Hello World"),
            ...
        ]

class TestMyFunc(autograding.TestFunc):
    def setUp(self):
        import main
        self.testcases = [
            case.FuncCall(func=main.myfunc, args=("arg1", "arg2"), result=42),
            ...
        ]


if __name__ == "__main__":
    unittest.main()
```
