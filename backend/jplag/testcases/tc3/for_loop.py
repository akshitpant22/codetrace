def sum_numbers(n):
    total = 0
    for i in range(n):
        total += i
    return total

def print_squares(n):
    squares = []
    for i in range(n):
        squares.append(i * i)
    return squares

def count_evens(n):
    count = 0
    for i in range(n):
        if i % 2 == 0:
            count += 1
    return count

print(sum_numbers(10))
print(print_squares(10))
print(count_evens(10))