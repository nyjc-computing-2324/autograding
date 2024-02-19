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

    def test_docstring(self):
        tested_funcs = set()
        for test in self.testcases:
            if test.func in tested_funcs:
                continue
            self.assertTrue(hasattr(test.func, "__doc__"),
                        msg=f"{test.name()} has no docstring")
            self.assertTrue(test.func.__doc__,
                        msg=f"{test.name()} has no docstring")
            tested_funcs.add(test.func)

    def test_function_call(self):
        for test in self.testcases:
            with self.subTest(call=test.callstr()):
                result = test.func(*test.args)
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
                    msg=f"{test.callstr()} returned {result!r}, expected {test.ans!r}"
                )



if __name__ == '__main__':
    unittest.main()
