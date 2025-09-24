from graphlet.capture import auto_partition

@auto_partition
def full_program(a, b, c):
    # (+, *) parts will be captured; "**" stays in Python
    y1 = (a * b) + c            # captured -> compiled -> executed
    y2 = (a ** 2) + b           # '**' not captured, pure Python
    return y1 + y2

if __name__ == "__main__":
    print(full_program(2,3,5))  # => (2*3+5) + (2**2+3) = 11 + 7 = 18