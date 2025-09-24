from graphlet import Graph

def test_graph_build_and_dump():
    g = Graph()
    a = g.input("a"); b = g.input("b")
    t = g.add_op("add", a, b)
    g.set_outputs(t)
    s = g.dump()
    assert "add(a, b)" in s
    assert "outputs" in s