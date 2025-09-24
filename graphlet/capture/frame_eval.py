from __future__ import annotations
import ctypes
from contextlib import ContextDecorator

class EvalFrameContext(ContextDecorator):
    """Educational scaffold; swapping CPython eval frame is ABI/version-sensitive."""
    def __init__(self, eval_func):
        self.eval_func = eval_func
        self._orig = None

    def __enter__(self):
        PyEval_SetEvalFrame = getattr(ctypes.pythonapi, "PyEval_SetEvalFrame", None)
        if PyEval_SetEvalFrame is None:
            raise RuntimeError("PyEval_SetEvalFrame not available in this Python build.")
        PyEval_SetEvalFrame.restype = ctypes.py_object
        PyEval_SetEvalFrame.argtypes = [ctypes.py_object]
        self._orig = PyEval_SetEvalFrame(self.eval_func)
        return self

    def __exit__(self, exc_type, exc, tb):
        PyEval_SetEvalFrame = getattr(ctypes.pythonapi, "PyEval_SetEvalFrame", None)
        if PyEval_SetEvalFrame is not None:
            PyEval_SetEvalFrame(self._orig)
        return False