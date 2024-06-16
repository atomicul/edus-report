from typing import Callable, List


def options_select[T](options: List[T], *, key: Callable[[T], str] = lambda x: x) -> T:
    options_str = (key(o) for o in options)
    print(*(f"{i}) {var}" for i, var in enumerate(options_str, 1)), sep="\n")
    print()

    while True:
        try:
            i = int(input(f"Pick an option [1-{len(options)}]: "))
            return options[i - 1]
        except Exception:
            pass


def question(q: str, *, default: bool | None = None):
    while True:
        x = input(
            f"{q} [{'Y' if default is True else 'y'}/{'N' if default is False else 'n'}]: "
        )
        if x.lower() in ["y", "yes"]:
            return True
        if x.lower() in ["n", "no"]:
            return False
        if default is not None:
            return default
