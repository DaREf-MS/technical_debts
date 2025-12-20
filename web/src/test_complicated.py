# File used to add a complicated function to be evaluated for the cyclomatic complexity

def complicated_function(x, y):
    result = 0
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                result += i
            else:
                if y > 0:
                    result -= y
                else:
                    for j in range(abs(y)):
                        if j % 3 == 0:
                            result += j
                        else:
                            result -= j
    elif x == 0:
        if y == 0:
            result = 42
        else:
            result = -42
    else:
        while x < 0:
            result += x
            x += 1
    return result