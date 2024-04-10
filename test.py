def get_sum(*arg):
    total = 0
    for el in arg:
        total += get_sum(el)
    return total

print(get_sum([1, 2, 3]))
