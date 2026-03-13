# Day 1 - Python vs C++ first look

def describe_number(n):
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)

results = [describe_number(n) for n in range(1, 21)]

for result in results:
    print(result)