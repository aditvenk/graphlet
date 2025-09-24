from graphlet.capture.region_jit import region_jit

@region_jit
def full_program(a, b, c):
    # The (+,*) parts are captured and optimized; (**) runs in Python.
    y1 = (a * b) + c     # captured region
    y2 = (a ** 2) + b    # fallback to Python for "**"
    return y1 + y2       # result of both is combined

if __name__ == "__main__":
    print(full_program(2,3,5))  # (2*3+5)=11, (2**2+3)=7 => 18