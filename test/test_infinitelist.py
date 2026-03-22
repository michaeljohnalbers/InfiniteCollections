import unittest
from typing import Any

import pytest

from infinitecollections.list import InfiniteList


class InfiniteListTest(unittest.TestCase):
    def test_infinitelist_is_list(self) -> None:
        integer_list: InfiniteList[int] = InfiniteList()
        self.assertIsInstance(integer_list, list)

        str_list: InfiniteList[str] = InfiniteList()
        self.assertIsInstance(str_list, list)

    def test_construction(self) -> None:
        test_list: InfiniteList[Any] = InfiniteList()
        self.assertEqual(0, len(test_list))
        # TODO: add more tests as more stuff is implemented

    def test_append(self) -> None:
        integer_list: InfiniteList[int] = InfiniteList()
        for x in range(0, 100):
            integer_list.append(x)
            self.assertEqual(x + 1, len(integer_list), f"Failed for x == {x}")

    def test__getitem(self) -> None:
        integer_list: InfiniteList[int] = InfiniteList()
        for x in range(0, 100):
            integer_list.append(x)
            self.assertEqual(x, integer_list[x], f"Failed for x == {x}")

        for x in range(-1, -99):
            self.assertEqual(99 + x, integer_list[x], f"Failed for x == {x}")

    def test__getitem_indexerror(self) -> None:
        integer_list: InfiniteList[int] = InfiniteList()
        for x in range(0, 100):
            integer_list.append(x)

        for index in [100, 101, 1000000, -100, -101, -400]:
            with pytest.raises(IndexError):
                integer_list[index]


if __name__ == "__main__":
    unittest.main()
