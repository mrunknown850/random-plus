from os import linesep
from sys import argv
from collections import deque
import random

# def randomString(length: int) -> str:

class ConstantInteger:
    def __init__(self, low: int, high: int) -> None:
        self.value: int = random.randint(low, high)
    def __repr__(self) -> int:
        return self.value
    
class RandomInteger:
    def __init__(self, low: int, high: int) -> None:
        self.low: int = low
        self.high: int = high
    def __repr__(self) -> int:
        return random.randint(self.low, self.high)

FILENAME = ""
CURRENT_LINE = 0

class InvalidKeyword(Exception):
    def __init__(self):
        super().__init__(f'File "{FILENAME}", line {CURRENT_LINE}')

def variable_tokenizer(variable_line: str) -> dict | None:
    global CURRENT_LINE
    CURRENT_LINE += 1
    
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
                    # If initializing a variable name
                    if keyword[0] == "%":
                        token['name'] = keyword[1:]
                        isCompleted = True
                    else:
                        raise InvalidKeyword
            continue
        if token['type'] == 'int':
            try:
                token['range'] = tuple( sorted( [int(words[num]), int(words[num+1]) ] ))
            except ValueError:
                raise InvalidKeyword
            break
        

    if 'isConst' not in token.keys():
        token['isConst'] = False

    return token

def layout_tokenizer(line_stack: list) -> tuple | None:
    global CURRENT_LINE

    IS_VERTICAL = False
    IS_HORIZONTAL = False
    
    tokens = []
    currentToken = {}

    for index, line in enumerate(line_stack):
        CURRENT_LINE += 1
        # Removing the \n at the end of every line
        line = line.replace('\n', '')

        # Spliting the line to words
        words = line.split()
        if len(words) == 0:
            continue

        # TRUTH TABLE
        if not IS_VERTICAL and not IS_HORIZONTAL:
            # * Both VERTICAL and HORIZONTAL are available
            match words[0]:
                case 'vertical':
                    IS_VERTICAL = True

                    currentToken['type'] = 'v-array'
                    currentToken['contain'] = []

                    if words[1][0] == "$":
                        currentToken['length'] = words[1][1:]
                    else:
                        try:
                            currentToken['length'] = int(words[1])
                        except ValueError:
                            raise InvalidKeyword
                case 'horizontal':
                    IS_HORIZONTAL = True

                    currentToken['type'] = {'h-array'}
                    currentToken['contain'] = []

                    if words[1][0] == "$":
                        currentToken['length'] = words[1][1:]
                    else:
                        try:
                            currentToken['length'] = int(words[1])
                        except ValueError:
                            raise InvalidKeyword
                case 'v-end':
                    raise InvalidKeyword
                case 'h-end':
                    raise InvalidKeyword
                case _:
                    currentToken['type'] = 'list'
                    currentToken['contain'] = []
                    for word in words:
                        if word[0] == "$":
                            currentToken['contain'].append({'type': 'var', 'value': word[1:]})
                        else:
                            currentToken['contain'].append({'type': 'const', 'value': word})
        elif IS_VERTICAL and not IS_HORIZONTAL:
            subToken = {}
            # * Only the HORIZONTAL is available
            match words[0]:
                case 'vertical':
                    raise InvalidKeyword
                case 'horizontal':
                    IS_HORIZONTAL = True

                    subToken['type'] = 'h-array'
                    subToken['contain'] = []

                    if words[1][0] == "$":
                        subToken['length'] = words[1][1:]
                    else:
                        try:
                            subToken['length'] = int(words[1])
                        except ValueError:
                            raise InvalidKeyword
                case 'v-end':
                    IS_VERTICAL = False
                case 'h-end':
                    raise InvalidKeyword
                case _:
                    subToken['type'] = 'list'
                    subToken['contain'] = []
                    for word in words:
                        if word[0] == "$":
                            subToken['contain'].append({'type': 'var', 'value': word[1:]})
                        else:
                            subToken['contain'].append({'type': 'const', 'value': word})
            if len(subToken) != 0:
                currentToken['contain'].append(subToken)
        elif not IS_VERTICAL and IS_HORIZONTAL:
            # * RAISE EXCEPTION
            raise InvalidKeyword
        elif IS_VERTICAL and IS_HORIZONTAL:
            subToken = {}
            # * Only the HORIZONTAL is available
            match words[0]:
                case 'vertical':
                    raise InvalidKeyword
                case 'horizontal':
                    raise InvalidKeyword
                case 'v-end':
                    raise InvalidKeyword
                case 'h-end':
                    IS_HORIZONTAL = False
                case _:
                    subToken['type'] = 'list'
                    subToken['contain'] = []
                    for word in words:
                        if word[0] == "$":
                            subToken['contain'].append({'type': 'var', 'value': word[1:]})
                        else:
                            subToken['contain'].append({'type': 'const', 'value': word})
            if len(subToken) != 0:
                currentToken['contain'][-1]['contain'].append(subToken)
        
        if not IS_HORIZONTAL and not IS_VERTICAL:
            tokens.append(currentToken)
            currentToken = {}
    return tuple(tokens)

def tokenizer(lines: deque) -> dict:
    global CURRENT_LINE
    variableTokens = []

    # * VARIABLE SECTION
    currentLine: str = lines.popleft()
    currentLine = currentLine.replace('\n', '')
    while currentLine != "BEGIN":
        returnToken = variable_tokenizer(currentLine)
        if returnToken is not None:
            variableTokens.append(returnToken)
        currentLine = lines.popleft()
        currentLine = currentLine.replace('\n', '')
    CURRENT_LINE += 1

    # * LAYOUT SECTION
    currentLine = lines.pop()
    while currentLine != "END":
        currentLine = lines.pop()
    layoutTokens = layout_tokenizer(list(lines))

    return tuple([variableTokens, layoutTokens])

def main(path: str):
    # Reading the file itself
    global FILENAME
    FILENAME = path
    with open(FILENAME, 'r') as f:
        lines = f.readlines()
    lines = deque(lines)
    tokens = tokenizer(lines)
    print()

if __name__ == "__main__":
    # Retrieving the given file path
    main(argv[1])