from __future__ import annotations
import ast, inspect, textwrap, types
from typing import Any, List
from ..compiler import Compiler
from ..runtime import execute
from .bytecode_capture import BytecodeCapturer

def __graphlet_eval__(fn, *args):
    """Capture -> compile -> execute a small lambda defined over (+, *)."""
    g = BytecodeCapturer().build_graph(fn, *args)
    g = Compiler().compile(g)
    # Map param names to arg values
    sig = inspect.signature(fn)
    bound = sig.bind_partial(*args); bound.apply_defaults()
    env = dict(bound.arguments)
    return execute(g, **env)

class _CapturableExpr(ast.NodeVisitor):
    """Checks if an expression tree is composed only of +, *, Names, and Constants."""
    def __init__(self):
        self.ok = True
    def visit_BinOp(self, node):
        if not isinstance(node.op, (ast.Add, ast.Mult)):
            self.ok = False; return
        self.visit(node.left); self.visit(node.right)
    def visit_Name(self, node):
        pass
    def visit_Constant(self, node):
        pass
    def generic_visit(self, node):
        # Any other node makes it non-capturable
        self.ok = False

def _free_names(expr: ast.AST) -> List[str]:
    names = set()
    class V(ast.NodeVisitor):
        def visit_Name(self, node):
            names.add(node.id)
    V().visit(expr)
    return sorted(names)

class _WrapCapturable(ast.NodeTransformer):
    """Wrap capturable BinOp subtrees with __graphlet_eval__(lambda args: expr, *args)."""
    def visit_BinOp(self, node):
        node = self.generic_visit(node)  # transform children first
        checker = _CapturableExpr()
        checker.visit(node)
        if checker.ok:
            # Build lambda over the free names in this subexpr
            params = [ast.arg(arg=n) for n in _free_names(node)]
            lam = ast.Lambda(
                args=ast.arguments(posonlyargs=[], args=params, kwonlyargs=[], kw_defaults=[], defaults=[]),
                body=node,
            )
            call = ast.Call(
                func=ast.Name(id="__graphlet_eval__", ctx=ast.Load()),
                args=[lam] + [ast.Name(id=p.arg, ctx=ast.Load()) for p in params],
                keywords=[],
            )
            return call
        return node

def auto_partition(fn):
    """Decorator that partially captures (+,*) subexpressions inside a function.
    Unsupported parts (e.g., **, loops, I/O) run as normal Python.
    """
    src = inspect.getsource(fn)
    src = textwrap.dedent(src)
    mod = ast.parse(src)
    # Transform only the target function def
    class Rewriter(ast.NodeTransformer):
        def visit_FunctionDef(self, node: ast.FunctionDef):
            if node.name != fn.__name__:
                return node
            new_body = []
            wrapper = _WrapCapturable()
            for stmt in node.body:
                new_body.append(wrapper.visit(stmt))
            node.body = new_body
            return node
    mod = Rewriter().visit(mod)
    ast.fix_missing_locations(mod)

    # Compile into a new code object in a fresh namespace, injecting __graphlet_eval__
    ns = dict(fn.__globals__)
    ns["__graphlet_eval__"] = __graphlet_eval__
    code = compile(mod, filename=f"<auto_partition:{fn.__name__}>", mode="exec")
    exec(code, ns, ns)
    new_fn = ns[fn.__name__]
    new_fn.__name__ = f"autop_{fn.__name__}"
    new_fn.__doc__ = (fn.__doc__ or "") + "\n(Partially captured by graphlet: (+,*) subexpressions.)"
    return new_fn