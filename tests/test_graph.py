from graphlet import Graph
from graphlet.runtime import execute
import pytest

def test_graph_build_and_dump():
    g = Graph()
    a = g.input("a"); b = g.input("b")
    t = g.add_op("add", a, b)
    g.set_outputs(t)
    s = g.dump()
    assert "add(a, b)" in s
    assert "outputs" in s


def test_input_and_const_creation():
    g = Graph()
    a = g.input("a")
    c = g.const(7)
    assert a.op == "input" and a.name == "a"
    assert c.op == "const" and c.attrs.get("value") == 7
    # Each node is tracked in the graph
    assert a in g.nodes and c in g.nodes


def test_add_op_links_and_attrs():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    n = g.add_op("mul", a, b, commutative=True)
    assert n.op == "mul"
    assert n.inputs == [a, b]
    assert n.attrs.get("commutative") is True


def test_relink_builds_users_sets():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    t1 = g.add_op("add", a, b)
    t2 = g.add_op("mul", t1, a)
    g.relink()
    # users of `a` are t1 and t2 (via t2's input)
    assert t1 in a.users and t2 in a.users
    # users of `t1` is t2
    assert t2 in t1.users and t1 not in t1.users


def test_set_outputs_validation_and_dedup():
    g1 = Graph()
    g2 = Graph()
    a = g1.input("a")
    b = g1.input("b")
    t1 = g1.add_op("add", a, b)
    t2 = g1.add_op("mul", a, b)
    # Dedup preserves order
    g1.set_outputs(t1, t1, t2)
    assert g1.outputs == [t1, t2]
    # Foreign node should be rejected
    x = g2.input("x")
    with pytest.raises(ValueError):
        g1.set_outputs(t1, x)


def test_dump_includes_indices_and_outputs_line():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    t1 = g.add_op("add", a, b)
    t2 = g.add_op("mul", a, b)
    g.set_outputs(t1, t2)
    s = g.dump()
    lines = s.splitlines()
    # First lines list nodes with %index: repr
    assert lines[0].startswith("%0: ")
    assert lines[1].startswith("%1: ")
    # outputs line has indices of outputs
    assert lines[-1].startswith("outputs: ")
    assert "%" in lines[-1]


def test_node_equality_is_identity():
    g = Graph()
    a1 = g.input("a")
    a2 = g.input("a")  # same name, different object
    assert a1 is not a2
    assert (a1 == a2) is False  # eq=False yields object identity semantics
    assert (a1 == a1) is True


def test_add_op_rejects_foreign_inputs():
    g1 = Graph()
    g2 = Graph()
    a1 = g1.input("a1")
    x2 = g2.input("x2")
    with pytest.raises(ValueError):
        g1.add_op("add", a1, x2)


def test_relink_rejects_foreign_input_after_mutation():
    g1 = Graph()
    g2 = Graph()
    a1 = g1.input("a1")
    b1 = g1.input("b1")
    t = g1.add_op("add", a1, b1)
    x2 = g2.input("x2")
    # Simulate unsafe external mutation
    t.inputs[1] = x2
    with pytest.raises(ValueError):
        g1.relink()


def test_const_repr_in_dump():
    g = Graph()
    c = g.const(42)
    g.set_outputs(c)
    s = g.dump()
    assert "const(42)" in s


def test_execute_const_only():
    g = Graph()
    c = g.const(5)
    g.set_outputs(c)
    assert execute(g) == 5


def test_execute_simple_add_mul():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    c = g.input("c")
    t1 = g.add_op("mul", a, b)
    t2 = g.add_op("mul", a, c)
    out = g.add_op("add", t1, t2)  # a*b + a*c
    g.set_outputs(out)
    assert execute(g, a=2, b=3, c=4) == 2 * 3 + 2 * 4


def test_execute_multi_output_returns_tuple():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    s = g.add_op("add", a, b)
    p = g.add_op("mul", a, b)
    g.set_outputs(s, p)
    out_s, out_p = execute(g, a=2, b=3)
    assert out_s == 5 and out_p == 6


def test_execute_raises_on_missing_input():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    s = g.add_op("add", a, b)
    g.set_outputs(s)
    with pytest.raises(KeyError):
        execute(g, a=1)  # missing b


def test_execute_raises_on_unsupported_op():
    g = Graph()
    a = g.input("a")
    b = g.input("b")
    t = g.add_op("sub", a, b)  # runtime does not implement 'sub'
    g.set_outputs(t)
    with pytest.raises(NotImplementedError):
        execute(g, a=3, b=1)
