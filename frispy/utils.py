from termcolor import cprint
import re
from schema import Schema, SchemaError

from typing import Callable, List


def print_success(txt):
    cprint(txt, 'green')


def print_error(txt):
    cprint(txt, 'red')


def is_superset(superset, subset):
    try:
        Schema(subset, ignore_extra_keys=True).validate(superset)
        return True
    except SchemaError as err:
        # Convert SchemaError to AssertionError
        raise AssertionError({
            "message": err.args[0],
            "path": []
        })


def apply_function_on_splitted(path: List[str],
                               json,
                               func: Callable,
                               *args,
                               **kwargs):
    now = path[0] if path else None
    try:
        if now is None:
            return func(json, *args, **kwargs)
        if json is None:
            raise TypeError({
                "message": "reached null value",
                "path": [],
            })

        if now == '*' and isinstance(json, list):
            return all(apply_function_on_splitted(path[1:],
                                                  el,
                                                  func,
                                                  *args,
                                                  **kwargs)
                       for el in json)
        if now == '?' and isinstance(json, list):
            return any(apply_function_on_splitted(path[1:],
                                                  el,
                                                  func,
                                                  *args,
                                                  **kwargs)
                       for el in json)
        if now not in '*?':
            now = now.lstrip('\\')
            try:
                int_now = int(now)
                if isinstance(json, list) and int_now < len(json):
                    return apply_function_on_splitted(path[1:],
                                                      json[int_now],
                                                      func,
                                                      *args,
                                                      **kwargs)
            except ValueError:
                pass

            if isinstance(json, dict) and now in json:
                return apply_function_on_splitted(path[1:],
                                                  json[now],
                                                  func,
                                                  *args,
                                                  **kwargs)
            else:
                raise KeyError({
                    "message": "key not found",
                    "path": [],
                })

    except (AssertionError, TypeError, KeyError) as err:
        if now is not None:
            err.args[0]["path"].insert(0, now)
        raise err

    if now in '*?' and not isinstance(json, list):
        raise TypeError({
            "message": "is not a list",
            "path": [],
        })


def apply_function_on_path(path: str, json, func: Callable, *args, **kwargs):
    if path is None:
        return func(json, *args, **kwargs)

    splitted = re.split(r'(?<!\\)\.', path)
    splitted = [s.replace('\\.', '.') for s in splitted]

    return apply_function_on_splitted(splitted, json, func, *args, **kwargs)
