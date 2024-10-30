import re


class NumberNotFoundException(Exception):
    def __init__(self, response: str):
        super().__init__(f"No number in the range [0, 100] found in response: '{response}'")


def process_response(result: str) -> bool:
    if result.isdigit() and 0 <= int(result) <= 100:
        return 51 <= int(result) <= 100

    # You can skip this "workaround" and just raise an error
    match = re.search(r"(?<!-)\b([0-9]{1,2}|100)\b", result)
    if match:
        number = int(match.group())
        if 0 <= number <= 100:
            return 51 <= number <= 100

    raise NumberNotFoundException(result)
