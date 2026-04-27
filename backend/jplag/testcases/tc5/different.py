def fibonacci(n):
    result = []
    a = 0
    b = 1
    for i in range(n):
        result.append(a)
        temp = a + b
        a = b
        b = temp
    return result

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

print(fibonacci(10))
print(is_prime(17))
print(binary_search([1, 3, 5, 7, 9], 5))