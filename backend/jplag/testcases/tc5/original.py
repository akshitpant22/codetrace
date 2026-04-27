def is_palindrome(text):
    text = text.lower()
    cleaned = ""
    for char in text:
        if char.isalpha():
            cleaned += char
    return cleaned == cleaned[::-1]

def count_vowels(text):
    vowels = "aeiou"
    count = 0
    for char in text.lower():
        if char in vowels:
            count += 1
    return count

def reverse_string(text):
    result = ""
    for char in text:
        result = char + result
    return result

print(is_palindrome("racecar"))
print(count_vowels("hello world"))
print(reverse_string("python"))