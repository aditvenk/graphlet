from graphlet.capture import jit_capture

# This sub-function is in the capturable subset (add/mul/const/input).
@jit_capture
def captured_part(a, b, c):
    tmp = a * b
    out = tmp + c
    # dead work (will be removed by DCE inside jit_capture pipeline)
    _dead = (a * c) + tmp
    return out

def python_only(a, b):
    # Something our capturer doesn't support (e.g., exponentiation or a loop)
    return a ** 2 + b  # "**" not handled by capturer; stays in Python

def full_program(a, b, c):
    y1 = captured_part(a, b, c)   # captured -> optimized -> executed by graphlet
    y2 = python_only(a, b)        # runs under normal Python interpreter
    return y1 + y2                # stitched together in Python

if __name__ == "__main__":
    print(full_program(2, 3, 5))