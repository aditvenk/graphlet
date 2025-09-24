from __future__ import annotations
import dis
import inspect
from typing import Any, Dict, List, Callable
from ..graph import Graph
from ..compiler import Compiler
from ..runtime import execute

class BytecodeCapturer:
    """Walk Python bytecode for a small arithmetic subset and emit graphlet IR."""
    def _is_binary_add(self, instr: dis.Instruction) -> bool:
        return (instr.opname == "BINARY_ADD") or (instr.opname == "BINARY_OP" and instr.argrepr in ("+","ADD"))
    def _is_binary_mul(self, instr: dis.Instruction) -> bool:
        return (instr.opname == "BINARY_MULTIPLY") or (instr.opname == "BINARY_OP" and instr.argrepr in ("*","MULTIPLY"))

    def build_graph(self, fn, *call_args, **call_kwargs) -> Graph:
        sig = inspect.signature(fn)
        ba = sig.bind_partial(*call_args, **call_kwargs); ba.apply_defaults()

        g = Graph()
        inputs: Dict[str, Any] = {name: g.input(name) for name in sig.parameters.keys()}
        stack: List[Any] = []
        locals_env: Dict[str, Any] = {}

        for instr in dis.get_instructions(fn):
            op = instr.opname
            if op == "RESUME":  # Python 3.11+ artifact; no effect on stack.
                continue
            if op == "LOAD_FAST":
                name = instr.argval
                if name in locals_env:
                    stack.append(locals_env[name])
                else:
                    stack.append(inputs[name])
            elif op == "LOAD_CONST":
                stack.append(g.const(instr.argval))
            elif self._is_binary_add(instr):
                b = stack.pop(); a = stack.pop()
                stack.append(g.add_op("add", a, b))
            elif self._is_binary_mul(instr):
                b = stack.pop(); a = stack.pop()
                stack.append(g.add_op("mul", a, b))
            elif op == "STORE_FAST":
                locals_env[instr.argval] = stack.pop()
            elif op == "RETURN_VALUE":
                out = stack.pop()
                g.set_outputs(out)
                break
            else:
                raise NotImplementedError(f"Unsupported opcode: {op} ({instr.argrepr})")
        return g

def capture(fn):
    """Decorator: return a function that emits graph IR instead of executing."""
    capturer = BytecodeCapturer()
    def wrapped(*args, **kwargs):
        return capturer.build_graph(fn, *args, **kwargs)
    wrapped.__name__ = f"capture_{fn.__name__}"
    return wrapped

def jit_capture(fn: Callable) -> Callable:
    """Decorator: capture -> compile -> execute. Falls back to Python if capture fails.
    Useful for hybrid programs where unsupported pieces keep running in Python.
    """
    capturer = BytecodeCapturer()
    compiler = Compiler()

    def wrapped(*args, **kwargs):
        try:
            g = capturer.build_graph(fn, *args, **kwargs)
            g = compiler.compile(g)
            # map arg names to values for execute()
            sig = inspect.signature(fn)
            bound = sig.bind_partial(*args, **kwargs); bound.apply_defaults()
            env = dict(bound.arguments)
            return execute(g, **env)
        except NotImplementedError:
            # fallback: run original Python
            return fn(*args, **kwargs)
    wrapped.__name__ = f"jit_{fn.__name__}"
    return wrapped