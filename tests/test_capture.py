from graphlet.capture import capture, jit_capture
from graphlet import Compiler

@capture
def foo(a, b, c):
    tmp = a * b
    out = tmp + c
    dead = (a * c) + tmp
    return out

def test_bytecode_capture_and_dce():
    g = foo(1,2,3)
    assert any(n.op == "mul" for n in g.nodes)
    assert any(n.op == "add" for n in g.nodes)
    cg = Compiler().compile(g)
    dump = cg.dump()
    assert "add(mul(a, c), mul(a, b))" not in dump

@jit_capture
def bar(a, b, c):
    tmp = a * b
    return tmp + c

def test_jit_capture_executes():
    # Should return a Python value (captured -> compiled -> executed)
    out = bar(2,3,5)
    assert out == (2*3)+5