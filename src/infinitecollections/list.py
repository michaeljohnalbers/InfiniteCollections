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
    """
    Implementation of 'list' which can offload data to the hard drive in case of excessive memory usage.

    This class is NOT thread-safe.

    This class should not be considered secure in terms of making sure the data offloaded to disk cannot
    be accessed by unwanted parties. Efforts are made towards that effect, but no guarantees are made.
    """

    class __Chunk(Generic[S]):
        """
        Class used to partition the overall list into smaller pieces. Each chunk can be offloaded to the
        hard drive to save memory. When needed, the data can then be brought into memory. The class
        keeps track of the start and end indices (inclusive and exclusive, respectively) of the data in the overall list.

        This class does NOT support negative indices. It is up to the user of the class to convert all negative
        indices into non-negative values.
        """

        def __init__(self, start_index: int, max_chunk_size: int) -> None:
            self.data: list[S] = []
            #  TODO: try to make it based on memory space used
            self.capacity: int = max_chunk_size
            self.end_index: int = start_index
            self.max_chunk_size = max_chunk_size
            self.start_index: int = start_index

        def append(self, value: S) -> None:
            """
            Add the provided element to the end of this chunk. It is up to the caller to ensure that this chunk
            should be the one to store the element.
            :param value: Value to store
            """
            assert not self.full()  # Just in case
            self.end_index += 1
            self.data.append(value)

        def full(self) -> bool:
            """
            Is this current chunk full? That is, is it storing the maximum number of elements possible?
            :return: True if full, False otherwise
            """
            return self.end_index == (self.start_index + self.max_chunk_size)

        def has_index(self, index: int) -> bool:
            """
            Does this chunk have an element for the provided index?
            :param index: List index
            :return: True if the element at the index exists, False otherwise
            """
            return self.start_index <= index < self.end_index

        def should_have_index(self, index: int) -> bool:
            """
            Given an index, should this chunk contain an element at the index? The index does not necessarily
            have to actually have an element.
            :param index: List index
            :return: True if this chunk should be the chunk to store the element at the given index, False otherwise
            """
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
        """
        Standard bounds checking ensuring the provided index is within the overall bounds of the list.
        This supports any index value (including negative indices).
        :param index: Index to check
        :raise IndexError: If the index is out of bounds
        """
        end_index: int = -1
        if len(self.chunks) > 0:
            end_index = self.chunks[-1].end_index

        index_int = index.__index__()
        if (index_int >= 0 and index_int >= end_index) or (
            index_int < 0 and index_int < self.__abs_index(index).__index__()
        ):
            raise IndexError("list index out of range")

    def __create_chunk(self, start_index: SupportsIndex) -> InfiniteList.__Chunk[T]:
        """
        Create a new chunk at the end of the current set of chunks.
        :param start_index: Starting index of the new chunk (inclusive)
        :return: Newly created chunk
        """
        self.chunks.append(
            InfiniteList.__Chunk[T](start_index.__index__(), self.max_chunk_size)
        )
        return self.chunks[-1]

    def __get_chunk(self, index: SupportsIndex) -> InfiniteList.__Chunk[T]:
        """
        Returns the chunk which holds the value at the given index. If the chunk doesn't exist yet,
        it will be created.
        :param index: List index
        :return: Chunk for the given index
        """
        next_start_index: int = 0
        if index.__index__() < 0:
            index = self.__abs_index(index.__index__())
        # TODO: binary search if size > some crossover value
        for c in self.chunks:
            next_start_index = c.end_index
            if c.should_have_index(index.__index__()):
                return c
        return self.__create_chunk(next_start_index)

    def __get_last_chunk(self) -> InfiniteList.__Chunk[T]:
        """
        Get the chunk for the end of the list. If no exists, a new one will be created. If the last chunk
        is full, create a new chunk and return that. This function is mainly to support appending new data.
        :return: Last chunk for the list
        """
        if len(self.chunks) == 0:
            return self.__create_chunk(0)
        last_chunk = self.chunks[-1]
        if last_chunk.full():
            last_chunk = self.__create_chunk(last_chunk.end_index)
        return last_chunk

    def __abs_index(self, index: SupportsIndex) -> SupportsIndex:
        """
        Get the greater-than-zero value for any index value (positive or negative)
        :arg index: Index to convert to non-negative value
        :return: index value
        """
        if index.__index__() < 0:
            # TODO: this `len` is probably going to be pretty slow (may need to track last index w/ instance variable)
            index = len(self) + index.__index__()
        return index
