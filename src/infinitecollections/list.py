import typing
from typing import (
    Generic,
    NotRequired,
    SupportsIndex,
    TypedDict,
    TypeVar,
    Unpack,
    overload,
    override,
)

T = TypeVar("T")
S = TypeVar("S")


class InfiniteListKwargs(TypedDict):
    max_chunk_size: NotRequired[int]


class InfiniteList(list[T]):
    """Implementation of 'list' which can offload data to the hard drive in case of excessive memory usage."""

    class __Chunk(Generic[S]):
        def __init__(self, start_index: int, max_chunk_size: int) -> None:
            # TODO: change to tree for faster searching
            self.data: list[S] = []
            #  TODO: try to make it based on memory space used
            self.capacity: int = max_chunk_size
            self.end_index: int = start_index
            self.max_chunk_size = max_chunk_size
            self.start_index: int = start_index

        def append(self, value: S) -> None:
            assert not self.full()
            self.end_index += 1
            self.data.append(value)

        def full(self) -> bool:
            return self.end_index == (self.start_index + self.max_chunk_size)

        def has_index(self, index: int) -> bool:
            return self.start_index <= index < self.end_index

        def should_have_index(self, index: int) -> bool:
            return self.start_index <= index < (self.start_index + self.max_chunk_size)

        def __getitem__(self, index: int) -> S:
            return self.data[index - self.start_index]

        def __iter__(self) -> typing.Iterator[S]:
            yield from self.data

        def __len__(self) -> int:
            return len(self.data)

        @override
        def __str__(self) -> str:
            return ", ".join(d.__str__() for d in self.data)

    def __init__(self, **kwargs: Unpack[InfiniteListKwargs]) -> None:
        super().__init__()
        self.max_chunk_size: int = kwargs.get("max_chunk_size", 10)
        self.chunks: list[InfiniteList.__Chunk[T]] = []

    @override
    def append(self, value: T, /) -> None:
        chunk = self.__get_last_chunk()
        chunk.append(value)

    @overload
    def __getitem__(self, item: SupportsIndex, /) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: SupportsIndex | slice) -> T | list[T]:
        if isinstance(index, slice):
            # TODO: handle slice
            return []
        else:
            self.__bounds_check(index)
            chunk = self.__get_chunk(index)
            return chunk[index.__index__()]

    @override
    def __len__(self) -> int:
        return sum(len(c) for c in self.chunks)

    @override
    def __str__(self) -> str:
        return "[" + ", ".join(c.__str__() for c in self.chunks) + "]"

    def __bounds_check(self, index: SupportsIndex) -> None:
        end_index: int = -1
        if len(self.chunks) > 0:
            end_index = self.chunks[-1].end_index

        index_int = index.__index__()
        if (index_int >= 0 and index_int >= end_index) or (
            index_int < 0 and index_int < self.__positive_index(index).__index__()
        ):
            raise IndexError("list index out of range")

    def __create_chunk(self, start_index: SupportsIndex) -> InfiniteList.__Chunk[T]:
        self.chunks.append(
            InfiniteList.__Chunk[T](start_index.__index__(), self.max_chunk_size)
        )
        return self.chunks[-1]

    def __get_chunk(self, index: SupportsIndex) -> InfiniteList.__Chunk[T]:
        next_start_index: int = 0
        if index.__index__() < 0:
            index = self.__positive_index(index.__index__())
        for c in self.chunks:
            next_start_index = c.end_index
            if c.should_have_index(index.__index__()):
                return c
        return self.__create_chunk(next_start_index)

    def __get_last_chunk(self) -> InfiniteList.__Chunk[T]:
        if len(self.chunks) == 0:
            return self.__create_chunk(0)
        last_chunk = self.chunks[-1]
        if last_chunk.full():
            last_chunk = self.__create_chunk(last_chunk.end_index)
        return last_chunk

    def __positive_index(self, index: SupportsIndex) -> SupportsIndex:
        if index.__index__() < 0:
            # TODO: this is probably going to be pretty slow (may need to track last index w/ instance variable)
            index = len(self) + index.__index__()
        return index
