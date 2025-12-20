"""file_b.py - Simple code duplication demo"""


def duplicate_one():
    """This function is duplicated from file_a.py"""
    text = "Lorem ipsum"
    return text.lower()


def duplicate_two():
    """This function is duplicated from file_a.py"""
    numbers = [1, 2, 3]
    total = 0
    for n in numbers:
        total += n
    return total


def duplicate_three():
    """This function is duplicated from file_a.py"""
    data = {"name": "Lorem", "value": 42}
    return f"{data['name']}: {data['value']}"


def unique_function_b():
    """This function is unique to file_b"""
    items = ["Sit", "Amet", "Consectetur"]
    result = []
    for item in items:
        result.append(item.lower())
    return result


if __name__ == "__main__":
    print("=== file_b.py ===")
    print("duplicate_one():", duplicate_one())
    print("duplicate_two():", duplicate_two())
    print("duplicate_three():", duplicate_three())
    print("unique_function_b():", unique_function_b())
