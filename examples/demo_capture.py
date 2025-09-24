from graphlet.capture import capture
from graphlet import Compiler

@capture
def foo(a, b, c):
    tmp = a * b
    out = tmp + c
    dead = (a * c) + tmp
    return out

if __name__ == "__main__":
    g = foo(1,2,3)
    print("=== Captured Graph ==="); print(g.dump())
    from graphlet import Compiler
    g2 = Compiler().compile(g)
    print("\n=== After Compiler (DCE) ==="); print(g2.dump())