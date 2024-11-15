from typing import AsyncGenerator, Iterable


async def async_gen[T](gen: Iterable[T]) -> AsyncGenerator[T]:
    for element in gen:
        yield element
