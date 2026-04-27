def get_largest(data):
    largest = data[0]
    i = 1
    while i < len(data):
        if data[i] > largest:
            largest = data[i]
        i += 1
    return largest

def get_smallest(data):
    smallest = data[0]
    i = 1
    while i < len(data):
        if data[i] < smallest:
            smallest = data[i]
        i += 1
    return smallest

def get_spread(data):
    return get_largest(data) - get_smallest(data)

def check_ordered(data):
    i = 0
    while i < len(data) - 1:
        if data[i] > data[i + 1]:
            return False
        i += 1
    return True

data = [3, 1, 4, 1, 5, 9, 2, 6]
print(get_largest(data))
print(get_smallest(data))
print(get_spread(data))
print(check_ordered(data))