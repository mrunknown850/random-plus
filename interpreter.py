from os import linesep
from sys import argv
from collections import deque

def variable_tokenizer(variable_line: str) -> dict | None:
    token = {}
    words = variable_line.split()

    if len(words) == 0:
        return None

    isCompleted = False
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
            token['range'] = tuple( [int(words[num]), int(words[num+1][:-1]) ])
            break
        
    if 'isConst' not in token.keys():
        token['isConst'] = False

    return token

def layout_tokenizer(line_stack: list) -> tuple | None:
    tokens = []

    for index, line in enumerate(line_stack):
        # Logic for processing the 2 built-in variables
        if 'vertical' in line or 'horizontal' in line:
            pass
        else:
            # Breaking up the lines
            words = line.split()
            # for word in words:
    
    
    return tuple(tokens)

def tokenizer(lines: deque) -> dict:
    variableTokens = []

    # Scanning until reaching 
    currentLine: str = lines.popleft()
    currentLine = currentLine.replace('\n', '')
    while currentLine != "<":
        returnToken = variable_tokenizer(currentLine)
        if returnToken is not None:
            variableTokens.append(returnToken)
        currentLine = lines.popleft()
        currentLine = currentLine.replace('\n', '')
    lines.pop()
    layoutTokens = layout_tokenizer(list(lines))

    return tuple(variableTokens, layout_tokenizer)

def main(path: str):
    # Reading the file itself
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = deque(lines)
    tokens = tokenizer(lines)

if __name__ == "__main__":
    # Retrieving the given file path
    main(argv[1])