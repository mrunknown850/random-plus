"""Important library for the interpreter"""

from sys import argv
from os import chmod
from collections import deque

# from enum import Enum
import random

ALPHABET = "qwertyuiopasdfghjklzxcvbnm"
FILENAME = ""
CURRENT_LINE = 0

path = argv[1]

class ConstantString:
    """A class to define an initialy randomized string."""

    def __init__(self, length: int) -> None:
        self.value: str = "".join(random.choices(ALPHABET, k=length))

    def __repr__(self) -> str:
        return self.value


class RandomString:
    """A class to define a randomized string."""

    def __init__(self, length: int) -> None:
        self.length = length

    @property
    def value(self) -> str:
        return "".join(random.choices(ALPHABET, k=self.length))


class ConstantInteger:
    """A class to define an initialy randomized integer."""

    def __init__(self, low: int, high: int) -> None:
        self.value: int = random.randint(low, high)

    def __repr__(self) -> int:
        return self.value


class RandomInteger:
    """A class to define a randomized string."""

    def __init__(self, low: int, high: int) -> None:
        self.low: int = low
        self.high: int = high

    @property
    def value(self):
        return random.randint(self.low, self.high)


class InvalidKeyword(Exception):
    """Exception for InvalidKeyword"""

    def __init__(self):
        super().__init__(f'File "{FILENAME}", line {CURRENT_LINE}')


def classify_variable(variable_token: tuple) -> dict:
    """A basic function that turn tokens into pre-defined objects"""
    output = {}
    for token in variable_token:
        if token["isConst"]:
            if token["type"] == "int":
                output[token["name"]] = ConstantInteger(
                    token["range"][0], token["range"][1]
                )
            elif token["type"] == "str":
                output[token["name"]] = ConstantString(token["length"])
        else:
            if token["type"] == "int":
                output[token["name"]] = RandomInteger(
                    token["range"][0], token["range"][1]
                )
            elif token["type"] == "str":
                output[token["name"]] = RandomString(token["length"])
    return output


def variable_tokenizer(variable_line: str) -> dict | None:
    """Tokenized from the raw text"""
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
                    token["isConst"] = True
                case "int":
                    token["type"] = "int"
                case "str":
                    token["type"] = "str"
                case _:
                    # If initializing a variable name
                    if keyword[0] == "%":
                        token["name"] = keyword[1:]
                        isCompleted = True
                    else:
                        raise InvalidKeyword
            continue
        if token["type"] == "int":
            try:
                token["range"] = tuple(sorted([int(words[num]), int(words[num + 1])]))
            except ValueError as exc:
                raise InvalidKeyword from exc
            break
        elif token["type"] == "str":
            try:
                token["length"] = int(words[num])
            except ValueError as exc:
                raise InvalidKeyword from exc
            break

    if "isConst" not in token.keys():
        token["isConst"] = False

    return token


def layout_tokenizer(line_stack: list) -> tuple | None:
    """Tokenize the layout section"""
    global CURRENT_LINE

    IS_VERTICAL = False
    IS_HORIZONTAL = False

    tokens = []
    current_token = {}

    for line in line_stack:
        CURRENT_LINE += 1
        # Removing the \n at the end of every line
        line = line.replace("\n", "")

        # Spliting the line to words
        words = line.split()
        if len(words) == 0:
            continue

        # TRUTH TABLE
        if not IS_VERTICAL and not IS_HORIZONTAL:
            # * Both VERTICAL and HORIZONTAL are available
            match words[0]:
                case "vertical":
                    IS_VERTICAL = True

                    current_token["type"] = "v-array"
                    current_token["contain"] = []

                    if words[1][0] == "$":
                        current_token["length"] = words[1][1:]
                    else:
                        try:
                            current_token["length"] = int(words[1])
                        except ValueError as exc:
                            raise InvalidKeyword from exc
                case "horizontal":
                    IS_HORIZONTAL = True

                    current_token["type"] = "h-array"
                    current_token["contain"] = []

                    if words[1][0] == "$":
                        current_token["length"] = words[1][1:]
                    else:
                        try:
                            current_token["length"] = int(words[1])
                        except ValueError as exc:
                            raise InvalidKeyword from exc
                case "v-end":
                    raise InvalidKeyword from exc
                case "h-end":
                    raise InvalidKeyword from exc
                case _:
                    current_token["type"] = "list"
                    current_token["contain"] = []
                    for word in words:
                        if word[0] == "$":
                            current_token["contain"].append(
                                {"type": "var", "value": word[1:]}
                            )
                        else:
                            current_token["contain"].append(
                                {"type": "const", "value": word}
                            )
        elif IS_VERTICAL and not IS_HORIZONTAL:
            subToken = {}
            # * Only the HORIZONTAL is available
            match words[0]:
                case "vertical":
                    raise InvalidKeyword from exc
                case "horizontal":
                    IS_HORIZONTAL = True

                    subToken["type"] = "h-array"
                    subToken["contain"] = []

                    if words[1][0] == "$":
                        subToken["length"] = words[1][1:]
                    else:
                        try:
                            subToken["length"] = int(words[1])
                        except ValueError as exc:
                            raise InvalidKeyword from exc
                case "v-end":
                    IS_VERTICAL = False
                case "h-end":
                    raise InvalidKeyword from exc
                case _:
                    subToken["type"] = "list"
                    subToken["contain"] = []
                    for word in words:
                        if word[0] == "$":
                            subToken["contain"].append(
                                {"type": "var", "value": word[1:]}
                            )
                        else:
                            subToken["contain"].append({"type": "const", "value": word})
            if len(subToken) != 0:
                current_token["contain"].append(subToken)
        elif not IS_VERTICAL and IS_HORIZONTAL:
            subToken = {}
            # * Only the HORIZONTAL is available
            match words[0]:
                case "vertical":
                    raise InvalidKeyword from exc
                case "horizontal":
                    raise InvalidKeyword from exc
                case "v-end":
                    raise InvalidKeyword from exc
                case "h-end":
                    IS_HORIZONTAL = False
                case _:
                    subToken["type"] = "list"
                    subToken["contain"] = []
                    for word in words:
                        if word[0] == "$":
                            subToken["contain"].append(
                                {"type": "var", "value": word[1:]}
                            )
                        else:
                            subToken["contain"].append({"type": "const", "value": word})
            if len(subToken) != 0:
                current_token["contain"].append(subToken)
        elif IS_VERTICAL and IS_HORIZONTAL:
            subToken = {}
            # * Only the HORIZONTAL is available
            match words[0]:
                case "vertical":
                    raise InvalidKeyword from exc
                case "horizontal":
                    raise InvalidKeyword from exc
                case "v-end":
                    raise InvalidKeyword from exc
                case "h-end":
                    IS_HORIZONTAL = False
                case _:
                    subToken["type"] = "list"
                    subToken["contain"] = []
                    for word in words:
                        if word[0] == "$":
                            subToken["contain"].append(
                                {"type": "var", "value": word[1:]}
                            )
                        else:
                            subToken["contain"].append({"type": "const", "value": word})
            if len(subToken) != 0:
                current_token["contain"][-1]["contain"].append(subToken)

        if not IS_HORIZONTAL and not IS_VERTICAL:
            tokens.append(current_token)
            current_token = {}
    return tuple(tokens)


def tokenizer(lines: deque) -> dict:
    global CURRENT_LINE
    variableTokens = []

    # * VARIABLE SECTION
    currentLine: str = lines.popleft()
    currentLine = currentLine.replace("\n", "")
    while currentLine != "BEGIN":
        returnToken = variable_tokenizer(currentLine)
        if returnToken is not None:
            variableTokens.append(returnToken)
        currentLine = lines.popleft()
        currentLine = currentLine.replace("\n", "")
    CURRENT_LINE += 1

    # * LAYOUT SECTION
    currentLine = lines.pop()
    while currentLine != "END":
        currentLine = lines.pop()
    layoutTokens = layout_tokenizer(list(lines))

    return tuple([variableTokens, layoutTokens])


def single_vertical_array_generate(sub_token: list, variable_token: dict) -> str:
    for token in sub_token:
        current_line: str = ""
        if token["type"] == "list":
            for sub_token in token["contain"]:
                if sub_token["type"] == "var":
                    current_line += str(variable_token[sub_token["value"]].value) + " "
                elif sub_token["type"] == "const":
                    current_line += str(sub_token["value"]) + " "
            return current_line[:-1]
        if token["type"] == "h-array":
            if isinstance(token["length"], str):
                cycle_count = variable_token[token["length"]].value
            elif type(token["length"]) == int:
                cycle_count = token["length"]
            # Cycling through each iteration based on variabled time
            for cycle in range(cycle_count):
                for sub_token in token["contain"]:
                    for sub_sub_token in sub_token["contain"]:
                        if sub_sub_token["type"] == "var":
                            current_line += (
                                str(variable_token[sub_sub_token["value"]].value) + " "
                            )
                        elif sub_sub_token["type"] == "const":
                            current_line += str(sub_sub_token["value"]) + " "
            return current_line[:-1]


def generate(variable_token: dict, layout_token: tuple):
    lines = []
    for token in layout_token:
        current_line: str = ""

        # Processing line by line
        if token["type"] == "list":
            for sub_token in token["contain"]:
                if sub_token["type"] == "var":
                    current_line += str(variable_token[sub_token["value"]].value) + " "
                elif sub_token["type"] == "const":
                    current_line += str(sub_token["value"]) + " "
            lines.append(current_line[:-1])
        if token["type"] == "h-array":
            if isinstance(token["length"], str):
                cycle_count = variable_token[token["length"]].value
            elif isinstance((token["length"]), int):
                cycle_count = token["length"]
            # Cycling through each iteration based on variabled time
            for cycle in range(cycle_count):
                for sub_token in token["contain"]:
                    for sub_sub_token in sub_token["contain"]:
                        if sub_sub_token["type"] == "var":
                            current_line += (
                                str(variable_token[sub_sub_token["value"]].value) + " "
                            )
                        elif sub_sub_token["type"] == "const":
                            current_line += str(sub_sub_token["value"]) + " "
            lines.append(current_line[:-1])
        elif token["type"] == "v-array":
            if isinstance(token["length"], str):
                cycle_count = variable_token[token["length"]].value
            elif isinstance(token["length"], int):
                cycle_count = token["length"]
            for cycle in range(cycle_count):
                lines.append(
                    single_vertical_array_generate(token["contain"], variable_token)
                )
    # EXTRA
    return lines


# def main(path: str):
#     # Reading the file itself
#     global FILENAME
#     FILENAME = path
#     with open(FILENAME, "r", encoding="UTF-8") as f:
#         lines = f.readlines()
#     lines = deque(lines)

#     # Getting the tokenized lines
#     variable_tokens, layout_tokens = tokenizer(lines)
#     variable_tokens = classify_variable(variable_tokens)

#     output_lines = generate(variable_tokens, layout_tokens)


#     final_string = ""
#     for line in output_lines:
#         final_string += line + "\n"

#     path = path.replace(".rnd", ".inp")
#     with open(path, "w", encoding="UTF-8") as f:
#         f.write(final_string[:-2])

#     chmod(path, 0o777)


def interpret():
    # Reading the file itself
    global path
    global FILENAME
    FILENAME = path
    with open(FILENAME, "r", encoding="UTF-8") as f:
        lines = f.readlines()
    lines = deque(lines)

    # Getting the tokenized lines
    variable_tokens, layout_tokens = tokenizer(lines)
    variable_tokens = classify_variable(variable_tokens)

    output_lines = generate(variable_tokens, layout_tokens)

    final_string = ""
    for line in output_lines:
        final_string += line + "\n"

    path = path.replace(".rnd", ".inp")
    with open(path, "w", encoding="UTF-8") as f:
        f.write(final_string[:-2])

    chmod(path, 0o777)
    print(f"Interpreted '{FILENAME}' to '{path}'")


# if __name__ == "__main__":
#     # Retrieving the given file path
#     interpret(argv[1])
