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
        self.assertEqual("[]", test_list.__str__())
        with pytest.raises(IndexError):
            test_list[0]
        # TODO: add more tests as more stuff is implemented

    def test_append(self) -> None:
        integer_list: InfiniteList[int] = InfiniteList(max_chunk_size=10)
        for x in range(0, 100):
            integer_list.append(x)
            self.assertEqual(x + 1, len(integer_list), f"Failed for x == {x}")

    def test__getitem(self) -> None:
        # Use non-nice chunk size (i.e., not a nice round number like 10)
        integer_list: InfiniteList[int] = InfiniteList(max_chunk_size=17)
        for x in range(0, 100):
            integer_list.append(x)
            self.assertEqual(x, integer_list[x], f"Failed for x == {x}")

        for x in range(-1, -99):
            self.assertEqual(99 + x, integer_list[x], f"Failed for x == {x}")

    def test__getitem_indexerror(self) -> None:
        integer_list: InfiniteList[int] = InfiniteList(max_chunk_size=10)
        for x in range(0, 100):
            integer_list.append(x)

        for index in [100, 101, 1000000, -100, -101, -400]:
            with pytest.raises(IndexError):
                integer_list[index]

    def test__str(self) -> None:
        max_chunk_size = 10
        integer_list: InfiniteList[int] = InfiniteList(max_chunk_size=max_chunk_size)
        self.assertEqual("[]", integer_list.__str__())
        expected_number_str = ""
        for i in range(max_chunk_size + 1):
            integer_list.append(i)
            expected_number_str += f"{i}, "
        expected_number_str = expected_number_str[0:-2]
        self.assertEqual("[" + expected_number_str + "]", integer_list.__str__())


if __name__ == "__main__":
    unittest.main()
