def sum_numbers(n):
    total = 0
    i = 0
    while i < n:
        total += i
        i += 1
    return total

def print_squares(n):
    squares = []
    i = 0
    while i < n:
        squares.append(i * i)
        i += 1
    return squares

def count_evens(n):
    count = 0
    i = 0
    while i < n:
        if i % 2 == 0:
            count += 1
        i += 1
    return count

print(sum_numbers(10))
print(print_squares(10))
print(count_evens(10))