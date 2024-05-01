from sys import argv
from collections import deque

# KEYWORDS = {'const', 'int', 'str', 'vertical', 'horizontal'}

def variable_tokens(variable_line: str) -> dict | None:
    token = {}
    if len(variable_line) == 0:
        return None

    isCompleted = False
    words = variable_line.split()
    for num, keyword in enumerate(words):
        if not isCompleted:
            match keyword:
                case "const":
                    token['isConst'] = True
                case "int":
                    token['type'] = 'int'
                case "str":
                    token['type'] = 'str'
                case _:
                    token['name'] = keyword[1:]
                    isCompleted = True
            continue
        if token['type'] == 'int':
            token['range'] = tuple([words[num], words[num+1]])
        
        
    # Load in the missing keys

    return token

def tokenizer(lines: deque) -> dict:
    tokens = []

    # Scanning until reaching 
    currentLine = lines.popleft()
    while currentLine != "<":
        returnToken = variable_tokens(currentLine)
        if returnToken is not None:
            tokens.append(returnToken)

    return tuple(tokens)

def main(path: str):
    # Reading the file itself
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = deque(lines)

if __name__ == "__main__":
    # Retrieving the given file path
    main(argv[1])