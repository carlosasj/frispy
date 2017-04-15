import re

from requests.models import Response as Resp
from typing import List

from .decorators import log_assertion
from .utils import print_success, print_error, apply_function_on_path, is_superset


class Response:
    expectations = []

    def __init__(self, title: str, response: Resp):
        self.title = title
        self.response = response

    def toss(self):
        count_success = len([1 for e in self.expectations if not e['error']])
        count_all = len(self.expectations)
        pfunc = print_error if count_success != count_all else print_success
        pfunc(f"{self.title} ({count_success}/{count_all})")
        for ex in self.expectations:
            pfunc = print_error if ex['error'] else print_success
            pfunc(f"\t{ex['expectation']}: {ex['message']}")
        print()

    def expectStatus(self, status_number: int):  # noqa: N802
        return self.expect_status(status_number)

    def expectStatusIn(self, status_numbers: List[int]):  # noqa: N802
        return self.expect_status_in(status_numbers)

    def expectHeader(self, key: str, content: str):  # noqa: N802
        return self.expect_header(key, content)

    def expectHeaderContains(self, key: str, content: str):  # noqa: N802
        return self.expect_header_contains(key, content)

    def expectHeaderToMatch(self, key: str, pattern: str):  # noqa: N802
        return self.expect_header_to_match(key, pattern)

    def expectJSON(self, path, json=None):
        assert path is not None and json is not None,\
            '"path" and "json" cannot be None at same time'
        if json is None:
            # This change was made because of Frisby's Docs:
            # expectJSON( [path], json )
            # where the first argument is optional, not the last
            path, json = json, path
        self.expect_json(path, json)

    @log_assertion()
    def expect_status(self, status_number: int, text=None):
        expectation = (text if text is not None
                       else f"Expect status to be {status_number}")
        assert self.response.status_code == status_number, {
            "expectation": expectation,
            "message": f"was {self.response.status_code}",
        }
        return {"expectation": expectation}

    @log_assertion()
    def expect_status_in(self, status_numbers: List[int], text=None):
        expectation = (text if text is not None
                       else f"Expect status to be in {status_numbers}")
        assert self.response.status_code in status_numbers, {
            "expectation": expectation,
            "message": f"was {self.response.status_code}",
        }
        return {"expectation": expectation}

    @log_assertion()
    def expect_header(self, key: str, content: str, text=None):
        expectation = (text if text is not None
                       else f"Expect header \"{key}\" to be \"{content}\"")
        assert key in self.response.headers, {
            "expectation": expectation,
            "message": f"header \"{key}\" does not exist in response",
        }
        assert self.response.headers[key] == content, {
            "expectation": expectation,
            "message": f"was \"{self.response.headers[key]}\"",
        }
        return {"expectation": expectation}

    @log_assertion()
    def expect_header_contains(self, key: str, content: str, text=None):
        expectation = (text if text is not None else
                       f"Expect header \"{key}\" to contains \"{content}\"")
        assert key in self.response.headers, {
            "expectation": expectation,
            "message": f"header \"{key}\" does not exist in response",
        }
        assert content in self.response.headers[key], {
            "expectation": expectation,
            "message": (f"\"{content}\" not found in "
                        f"\"{self.response.headers[key]}\""),
        }
        return {"expectation": expectation}

    @log_assertion()
    def expect_header_to_match(self, key: str, pattern: str, text=None):
        expectation = (text if text is not None
                       else f"Expect header \"{key}\" to match \"{pattern}\"")
        assert key in self.response.headers, {
            "expectation": expectation,
            "message": f"header \"{key}\" does not exist in response",
        }
        assert re.match(pattern, self.response.headers[key]), {
            "expectation": expectation,
            "message": (f"\"{self.response.headers[key]}\" do not match "
                        f"\"{pattern}\""),
        }
        return {"expectation": expectation}

    @log_assertion()
    def expect_json(self, path, json, text=None):
        temp_path = 'response' if path is None else f"\"{path}\""
        expectation = (text if text is not None else
                       f"Expect {temp_path} to be the declared JSON")
        try:
            apply_function_on_path(path, self.response.json(), is_superset, json)
        except (AssertionError, TypeError, KeyError) as err:
            err.args[0]["expectation"] = expectation
            if 'path' in err.args[0] and len(err.args[0]['path']) > 1:
                err.args[0]["message"] = ''.join([
                    err.args[0].get('message', ''),
                    ' (',
                    ' > '.join(map(str, err.args[0]['path'])),
                    ')'])
            raise err
        return {"expectation": expectation}


