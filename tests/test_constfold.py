from graphlet import Graph, Compiler

def test_constant_folding_add_mul():
    g = Graph()
    a = g.input("a")
    c2 = g.const(2)
    c3 = g.const(3)
    t = g.add_op("mul", c2, c3)   # -> const(6)
    y = g.add_op("add", t, a)     # -> add(const(6), a)
    g.set_outputs(y)

    cg = Compiler().compile(g)
    dump = cg.dump()
    assert "const(6)" in dump