def calculate_sum(numbers):
    total = 0
    for n in numbers:
        total += n
    return total

def calculate_average(numbers):
    if len(numbers) == 0:
        return 0
    total = calculate_sum(numbers)
    return total / len(numbers)

def find_min(numbers):
    min_val = numbers[0]
    for n in numbers:
        if n < min_val:
            min_val = n
    return min_val

def find_max(numbers):
    max_val = numbers[0]
    for n in numbers:
        if n > max_val:
            max_val = n
    return max_val

numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(calculate_sum(numbers))
print(calculate_average(numbers))
print(find_min(numbers))
print(find_max(numbers))