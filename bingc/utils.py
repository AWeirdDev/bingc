import asyncio
from typing import Callable, Awaitable, ParamSpec, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from .primp import Response

T = TypeVar("T")
P = ParamSpec("P")


def asyncify(f: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Asyncify a synchronous function.

    Args:
        f (Callable[P, T]): The function to async-ify.

    Returns:
        Callable[P, Awaitable[T]]: The async-ified function.
    """

    async def run(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(f, *args, **kwargs)

    return run


def raise_for_status(res: "Response") -> None:
    """Raises an exception if the response status code is not 2xx."""
    assert 200 <= res.status_code <= 299, f"Response ({res.status_code}):\n{res.text}"
