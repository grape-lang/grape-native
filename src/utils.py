def popFirst(list: list) -> tuple[any, list]:
    return (list[0], list[1:])

def charRange(start: str, stop: str) -> range:
    return (chr(n) for n in range(ord(start), ord(stop) + 1))

def truncateString(string: str, length: int = 6) -> str:
    string = string.split("\n")[0]
    return (string[:length] + '...') if len(string) > length else string