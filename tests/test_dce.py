from graphlet import Graph, Compiler, DeadCodeElimination

def build_dead_graph():
    g = Graph()
    a = g.input("a"); b = g.input("b"); c = g.input("c")
    t1 = g.add_op("mul", a, b)      # live
    out = g.add_op("add", t1, c)    # live
    d1 = g.add_op("mul", a, c)      # dead
    _  = g.add_op("add", d1, t1)    # dead
    g.set_outputs(out); return g

def test_dce_pass_direct():
    g = build_dead_graph()
    before = len(g.nodes)
    DeadCodeElimination().run(g)
    after = len(g.nodes)
    assert after < before
    dump = g.dump()
    assert "mul(a, c)" not in dump

def test_compiler_pipeline_runs_dce():
    g = build_dead_graph()
    cg = Compiler().compile(g)
    dump = cg.dump()
    assert "mul(a, c)" not in dump