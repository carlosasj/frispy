from termcolor import cprint
import re

from typing import Callable, List


def print_success(txt):
    cprint(txt, 'green')


def print_error(txt):
    cprint(txt, 'red')


def is_superset(superset, subset):
    assert type(superset) is type(subset), {
        "message": "different types",
        "path": [],
    }

    # Now we can check the type for superset only, because we know that
    # type(superset) is type(subset)

    if isinstance(superset, list):
        assert len(superset) == len(subset), {
            "message": f"lists with different sizes",
            "path": [],
        }
        for num, (superset_item, subset_item) in enumerate(zip(superset, subset)):
            try:
                val = is_superset(superset_item, subset_item)
                assert val, {
                    "message": f"error at iteration {num}",
                    "path": [],
                }
            except AssertionError as err:
                err.args[0]["path"].insert(0, num)
                raise err

    elif isinstance(superset, dict):
        for key in subset:
            assert key in superset, {
                "message": f"key \"{key}\" not found",
                "path": [key],
            }

            try:
                val = is_superset(superset[key], subset[key])
                assert val, {
                    "message":
                        f"values \"{str(superset[key])[:30]}"
                        f"{'...' if len(str(superset[key])) > 30 else ''}\" "
                        f"and \"{str(subset[key])[:30]}"
                        f"{'...' if len(str(subset[key])) > 30 else ''}\" "
                        f"differ for key \"{key}\"",
                    "path": [],
                }
            except AssertionError as err:
                err.args[0]["path"].insert(0, key)
                raise err

    else:
        assert superset == subset, {
            "message":
                f"values \"{str(superset)[:30]}"
                f"{'...' if len(str(superset)) > 30 else ''}\" "
                f"and \"{str(subset)[:30]}"
                f"{'...' if len(str(subset)) > 30 else ''}\" "
                f"differ",
            "path": [],
        }

    return True


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
