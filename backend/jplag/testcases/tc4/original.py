def find_max(numbers):
    max_val = numbers[0]
    for n in numbers:
        if n > max_val:
            max_val = n
    return max_val

def find_min(numbers):
    min_val = numbers[0]
    for n in numbers:
        if n < min_val:
            min_val = n
    return min_val

def find_range(numbers):
    return find_max(numbers) - find_min(numbers)

def is_sorted(numbers):
    for i in range(len(numbers) - 1):
        if numbers[i] > numbers[i + 1]:
            return False
    return True

numbers = [3, 1, 4, 1, 5, 9, 2, 6]
print(find_max(numbers))
print(find_min(numbers))
print(find_range(numbers))
print(is_sorted(numbers))