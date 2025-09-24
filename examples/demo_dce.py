from graphlet import Graph, Compiler

def build_graph():
    g = Graph()
    a = g.input("a"); b = g.input("b"); c = g.input("c")
    t1 = g.add_op("mul", a, b)
    y  = g.add_op("add", t1, c)
    d1 = g.add_op("mul", a, c)
    _  = g.add_op("add", d1, t1)
    g.set_outputs(y)
    return g

if __name__ == "__main__":
    g = build_graph()
    print("=== Before DCE ==="); print(g.dump())
    cg = Compiler().compile(g)
    print("\n=== After DCE ==="); print(cg.dump())