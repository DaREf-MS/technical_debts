"""file_a.py - Simple code duplication demo"""


def duplicate_one():
    """This function is duplicated in file_b.py"""
    text = "Lorem ipsum"
    return text.lower()


def duplicate_two():
    """This function is duplicated in file_b.py"""
    numbers = [1, 2, 3]
    total = 0
    for n in numbers:
        total += n
    return total


def duplicate_three():
    """This function is duplicated in file_b.py"""
    data = {"name": "Lorem", "value": 42}
    return f"{data['name']}: {data['value']}"


def unique_function_a():
    """This function is unique to file_a"""
    words = ["Lorem", "Ipsum", "Dolor"]
    result = []
    for word in words:
        result.append(word.upper())
    return result


if __name__ == "__main__":
    print("=== file_a.py ===")
    print("duplicate_one():", duplicate_one())
    print("duplicate_two():", duplicate_two())
    print("duplicate_three():", duplicate_three())
    print("unique_function_a():", unique_function_a())
