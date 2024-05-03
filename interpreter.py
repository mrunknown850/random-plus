from sys import argv
from collections import deque
import random

class ConstantString:
    def __init__(self, length: int) -> None:
        ALPHABET = "qwertyuiopasdfghjklzxcvbnm"
        self.value: str = ''.join(random.choices(ALPHABET, k=length))
    def __repr__(self) -> str:
        return self.value

class RandomString:
    def __init__(self, length: int) -> None:
        self.length = length
    @property
    def value(self) -> str:
        ALPHABET = "qwertyuiopasdfghjklzxcvbnm"
        return ''.join(random.choices(ALPHABET, k=self.length))

class ConstantInteger:
    def __init__(self, low: int, high: int) -> None:
        self.value: int = random.randint(low, high)
    def __repr__(self) -> int:
        return self.value
    
class RandomInteger:
    def __init__(self, low: int, high: int) -> None:
        self.low: int = low
        self.high: int = high
    @property
    def value(self):
        return random.randint(self.low, self.high)

FILENAME = ""
CURRENT_LINE = 0

class InvalidKeyword(Exception):
    def __init__(self):
        super().__init__(f'File "{FILENAME}", line {CURRENT_LINE}')

def classify_variable(variable_token: tuple) -> dict:
    output = {}
    for token in variable_token:
        if token['isConst']:
            if token['type'] == 'int':
                output[token['name']] = ConstantInteger(token['range'][0], token['range'][1])
            elif token['type'] == 'str':
                output[token['name']] = ConstantString(token['length'])
        else:
            if token['type'] == 'int':
                output[token['name']] = RandomInteger(token['range'][0], token['range'][1])
            elif token['type'] == 'str':
                output[token['name']] = RandomString(token['length'])
                pass
    return output

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
        elif token['type'] == 'str':
            try:
                token['length'] = int(words[num])
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

                    currentToken['type'] = 'h-array'
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
                currentToken['contain'].append(subToken)
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

def generate(variableToken: dict, layoutToken: tuple):
    lines = []
    for token in layoutToken:
        currentLine: str = ''
        
        # Processing line by line
        if token['type'] == 'list':
            for subToken in token['contain']:
                if subToken['type'] == 'var':
                    currentLine += str(variableToken[subToken['value']].value) + " "
                elif subToken['type'] == 'const':
                    currentLine += str(subToken['value']) + " "
            lines.append(currentLine[:-1])
        elif token['type'] == 'h-array':
            if type(token['length']) == str:
            # Cycling through each iteration based on variabled time
                for cycle in range(variableToken[token['length']].value):
                    for subToken in token['contain']:
                        for subSubToken in subToken['contain']:
                            if subSubToken['type'] == 'var':
                                currentLine += str(variableToken[subSubToken['value']].value) + " "
                            elif subSubToken['type'] == 'const':
                                currentLine += str(subSubToken['value']) + " "
                lines.append(currentLine[:-1])
    # EXTRA
    # for line in lines:
    #     print(line)
                

def main(path: str):
    # Reading the file itself
    global FILENAME
    FILENAME = path
    with open(FILENAME, 'r') as f:
        lines = f.readlines()
    lines = deque(lines)

    # Getting the tokenized lines
    variableTokens, layoutTokens = tokenizer(lines)
    variableTokens = classify_variable(variableTokens)

    print(generate(variableTokens, layoutTokens))


if __name__ == "__main__":
    # Retrieving the given file path
    main(argv[1])