from typing import Any, AsyncGenerator, Generator, Iterable


async def async_gen[T](gen: Iterable[T]) -> AsyncGenerator[T]:
    for element in gen:
        yield element


def flatten(value: Any) -> Any:
    if isinstance(value, str):
        yield value

    elif isinstance(value, Iterable) or isinstance(value, Generator):
        for element in value:
            yield flatten(element)

    else:
        yield value
