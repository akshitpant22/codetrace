def compute_total(items):
    result = 0
    for item in items:
        result += item
    return result

def compute_mean(items):
    if len(items) == 0:
        return 0
    result = compute_total(items)
    return result / len(items)

def get_minimum(data):
    smallest = data[0]
    for val in data:
        if val < smallest:
            smallest = val
    return smallest

def get_maximum(data):
    largest = data[0]
    for val in data:
        if val > largest:
            largest = val
    return largest

data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
print(compute_total(data))
print(compute_mean(data))
print(get_minimum(data))
print(get_maximum(data))