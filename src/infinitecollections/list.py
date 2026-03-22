from typing import Generic, SupportsIndex, TypeVar, overload, override

T = TypeVar("T")
S = TypeVar("S")


class InfiniteList(list[T]):
    """Implementation of 'list' which can offload data to the hard drive in case of excessive memory usage."""

    class __Chunk(Generic[S]):
        MAX_CHUNK_SIZE: int = 10

        def __init__(self, start_index: int) -> None:
            # TODO: change to tree for faster searching
            self.data: list[S] = []
            self.start_index: int = start_index
            self.end_index: int = start_index
            #  TODO: try to make it based on memory space used
            self.capacity: int = self.MAX_CHUNK_SIZE

        def append(self, value: S) -> None:
            assert not self.full()
            self.end_index += 1
            self.data.append(value)

        def full(self) -> bool:
            return self.end_index == (self.start_index + self.MAX_CHUNK_SIZE)

        def has_index(self, index: int) -> bool:
            return self.start_index <= index < self.end_index

        def should_have_index(self, index: int) -> bool:
            return self.start_index <= index < (self.start_index + self.MAX_CHUNK_SIZE)

        def __getitem__(self, index: int) -> S:
            return self.data[index - self.start_index]

        def __len__(self) -> int:
            return len(self.data)

        @override
        def __str__(self) -> str:
            return f"List chunk, [{self.start_index}, {self.end_index}), capacity: {self.capacity}"

    def __init__(self) -> None:
        super().__init__()
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

    def __bounds_check(self, index: SupportsIndex) -> None:
        end_index: int = -1
        if len(self.chunks) > 0:
            end_index = self.chunks[-1].end_index

        if (
            index.__index__() >= 0
            and index.__index__() >= end_index
            or index.__index__() < 0
            and index.__index__() < self.__positive_index(index).__index__()
        ):
            raise IndexError("list index out of range")

    def __create_chunk(self, start_index: SupportsIndex) -> InfiniteList.__Chunk[T]:
        self.chunks.append(InfiniteList.__Chunk[T](start_index.__index__()))
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
