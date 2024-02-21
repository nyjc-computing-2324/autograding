import subprocess
import unittest

from . import case

TIMEOUT = 3


class RuntimeError(Exception): ...


def strip_prompt(stdout: str, sep: str=":") -> str:
    """Strip the prompt from stdout.
    The prompt is assumed to end with a separator character (default=":"),
    followed by zero or more whitespace characters.
    """
    if stdout.strip() and (sep in stdout):
        stdout = stdout[stdout.find(sep) + 1:].lstrip()
    return stdout


def invoke_script(input_: str, script: str="main.py") -> str:
    """Invoke main.py and return its output."""
    # linebreak needed to trigger python input
    if not input_.endswith("\n"):
        input_ += "\n"
    result: subprocess.CompletedProcess = subprocess.run(
        ["python", script],
        input=input_,
        capture_output=True,
        text=True,
        timeout=TIMEOUT or 0,
    )
    stdout = result.stdout
    if result.stderr:
        raise RuntimeError(result.stderr)
    if not (stdout or stdout.strip()):
        return ""
    return strip_prompt(stdout) if ":" in stdout else stdout


class TestInputOutput(unittest.TestCase):
    """Test the input and output of main.py."""
    testcases: list[case.InOut]

    def setUp(self):
        raise AttributeError(
            f"{self.__class__.__name__} must implement setUp() to set testcases attribute"
        )

    def check_result(self, result: str, answer: str):
        """Test the user's answer against the expected answer."""
        if answer != "":
            self.assertNotEqual(result.strip(), "", msg="Error or no output from program.")
        self.assertIn(
            result,
            answer + "\n",
            msg=f"User output {result!r} != expected output {answer!r}"
        )

    def test_input_output(self):
        """Run test cases"""
        for input_, answer in self.testcases:
            with self.subTest(input=input_):
                self.check_result(invoke_script(input_), answer)


class TestFunction(unittest.TestCase):
    """Test a function call"""
    testcases: list[case.FuncCall]

    def setUp(self):
        raise AttributeError(
            f"{self.__class__.__name__} must implement setUp() to set testcases attribute"
        )

    def check_result(self, test, result):
        if test.ans is not None:
            self.assertIsNotNone(
                result,
                msg=f"{test.callstr()} returned None"
            )
        self.assertIsInstance(
            result, type(test.ans),
            msg=f"{test.callstr()} returned {type(result)}, expected {type(test.ans)}"
        )
        self.testcase.assertEqual(
            result, test.ans,
            msg=f"{test.callstr()}: Got {result!r}, expected {test.ans!r}"
        )

    def test_docstring(self):
        tested_funcs = set()
        for test in self.testcases:
            if test.func in tested_funcs:
                continue
            with self.subTest(function=test.name()):
                self.assertTrue(hasattr(test.func, "__doc__"),
                            msg=f"{test.name()} has no docstring")
                self.assertTrue(test.func.__doc__,
                            msg=f"{test.name()} has no docstring")
                tested_funcs.add(test.func)

    def test_function_call(self):
        for test in self.testcases:
            with self.subTest(call=test.callstr()):
                result = test.func(*test.args)
                self.check_result(test, result)


class TestRecursive(unittest.TestCase):
    """Test a recursive function call"""
    testcases: list[case.RecursiveCall]
    
    def setUp(self):
        raise AttributeError(
            f"{self.__class__.__name__} must implement setUp() to set testcases attribute"
        )
    
    def check_result(self, test: case.RecursiveCall, result):
        if test.ans is not None:
            self.assertIsNotNone(
                result,
                msg=f"{test.callstr()} returned None"
            )
        self.assertIsInstance(
            result, type(test.ans),
            msg=f"{test.callstr()} returned {type(result)}, expected {type(test.ans)}"
        )
        self.assertEqual(
            result, test.ans,
            msg=f"{test.callstr()}: Got {result!r}, expected {test.ans!r}"
        )

    def check_recursion(self, test: case.RecursiveCall):
        # Replace user function with wrapped function in `main` module
        # The wrapped function lets us trace input args and return values
        # of each recursive call
        inputargs = []
        retvals = []
        def wrapcall(func):
            """Wrapper that collects input args and return result from
            each recursive call into a closure list.
            """
            def inner(*args, **kwargs):
                inputargs.append(args[0])
                result = func(*args, **kwargs)
                retvals.append(result)
                return result
            return inner

        orig_func = getattr(test.module, test.func.__name__)
        wrapped_func = wrapcall(orig_func)
        setattr(test.module, test.func.__name__, wrapped_func)
        
        # Check requirements of recursive functions:
        # 1. Base case handled
        # 2. Function calls itself
        # 3. Each successive calls brings result closer to base case

        # 1
        try:
            result = orig_func(*test.args)
        except Exception as err:
            if test.basecase:
                raise RecursionError("Base case not handled")
            else:
                raise err
        # Replace original function after func call
        setattr(test.module, test.func.__name__, orig_func)

        # 2
        if not test.basecase:
            self.assertGreater(len(retvals),
                               1,  # ignore original call
                               f"{test.name()} does not call itself")
        # 3
        for i in range(len(inputargs) - 1):
            if isinstance(inputargs[i], (list, str)):
                self.assertLess(len(inputargs[i+1]), len(inputargs[i]),
                                f"Each successive call to reverse() should pass a shorter input")
            elif isinstance(inputargs[i], (int, float)):
                self.assertLess(inputargs[i+1], inputargs[i],
                    f"Each successive call to reverse() should pass a smaller value")
        # Check if result is correct
        self.check_result(test, result)

    def test_docstring(self):
        # Only test functions once; use a set to store tested functions
        tested_funcs = set()
        for test in self.testcases:
            if test.func in tested_funcs:
                continue
            tested_funcs.add(test.func)
            with self.subTest(function=test.name()):
                self.assertTrue(hasattr(test.func, "__doc__"),
                            msg=f"{test.name()} has no docstring")
                self.assertTrue(test.func.__doc__,
                            msg=f"{test.name()} has no docstring")

    def test_recursive_call(self):
        for test in self.testcases:
            with self.subTest(call=test.callstr()):
                self.check_recursion(test)
                


if __name__ == '__main__':
    unittest.main()
