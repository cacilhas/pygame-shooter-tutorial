from typing import Any, AsyncGenerator, Generator, Iterable


async def async_gen[T](gen: Iterable[T]) -> AsyncGenerator[T]:
    for element in gen:
        yield element
