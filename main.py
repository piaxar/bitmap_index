import time
import random
from collections import Counter
from bitarray import bitarray


def main():
    functionality_test()
    speed_test()


def functionality_test():
    # Testing index build, insertion, deletion,
    test_table = [
        Item(1, ['a', 'A']),
        Item(2, ['b', 'A']),
        Item(3, ['a', 'B'])
    ]

    index = BitmapIndex(test_table)
    print("Index after creating:\n", index)
    search_rules = [[0, 'a']]

    print("Search value 'a' in column #0 returns indexes :", index.get(search_rules))

    index.append(Item(4, ['a', 'A']))
    index.append(Item(5, ['b', 'B']))
    index.append(Item(6, ['C', 'D']))

    print("Index after adding elements:")
    print(index)

    print("Search value 'a' in column #0 returns indexes :", index.get(search_rules))

    index.delete(3)

    print("Index after deleting element:")
    print(index)


def speed_test():
    print("\nSpeed testing starts\n")
    long_list = get_long_list_of_items()
    avg_diff_time = []

    for i in range(1000, 21001, 1000):

        test_list = long_list[:i]
        print("Testing speed for list length = ", len(test_list))

        bitmap = BitmapIndex(test_list)
        item = test_list[random.randint(0, len(test_list))]

        start = time.time()
        result = naive_search(test_list, item)
        end = time.time()
        t_no_idx = end - start

        start = time.time()

        result = bitmap.get([(0, item.data[0]),  # using item to define a search rule
                             (1, item.data[1]),
                             (2, item.data[2]),
                             (3, item.data[3])])
        end = time.time()
        t_idx = end - start

        avg_diff_time.append(t_no_idx/t_idx)

    print("\n")
    print("In average, Index is {} times faster, than naive search".
          format(round(sum(avg_diff_time)/len(avg_diff_time)), 4))


class Item:
    """
    Class defining row in table
    ID is a unique value for internal purposes of db
    a = Item(id, ['a', 'A', 1, 'True'])
    """

    def __init__(self, key: int, data: list):
        self.key = key
        self.data = data

    def __str__(self):
        return "id: {}, data: {}".format(int(self.key), list(self.data))


class BitmapIndex:
    def __init__(self, table: list):
        self.length = len(table)
        self._build_index(table)
        self.table = table

    def _build_index(self, table):
        n_col = len(table[0].data)
        bit_columns = []
        names = []

        for i in range(n_col):
            # convert categorical values into bit arrays
            col = [row.data[i] for row in table]
            bit_col, n = self._col_to_bit_array(col)
            bit_columns.append(bit_col)
            names.append(n)

        self.bit_columns = bit_columns
        self.names = names

    @staticmethod
    def _col_to_bit_array(col: list):
        """
        Actual process of converting
        :return: bit_arrs - array of bit arrays for each unique value in column
                names - array of values which corresponds to bit_arrs by index
        """
        names = list(Counter(col).keys())
        bit_arrs = [bitarray() for _ in range(len(names))]
        for el in col:
            ind = names.index(el)
            for i, arr in enumerate(bit_arrs):
                arr.append(True if i == ind else False)
        return bit_arrs, names

    def get(self, conditions: list):
        """
        Returns set of row indexes, satisfying the condition
        :param conditions - list of condition [[column_index, value], [...], ...]
        condition format -> [column_index, value]
        """
        a = bitarray(self.length)
        a.setall(1)
        for condition in conditions:
            a &= self._get_bitarr(condition[0], condition[1])
        res = []
        for i, v in enumerate(a):
            if v==1: res.append(i)
        return res

    def delete(self, id):
        """
        Delete element by id
        """
        self.length -= 1
        self.table.pop(id)
        for columns in self.bit_columns:
            for column in columns:
                column.pop(id)

    def append(self, element):
        self.length += 1
        self.table.append(element)
        data = element.data
        for index, value in enumerate(data):
            if value not in self.names[index]:
                # new value for the column
                self._add_new_column_value(index, value)
            for col_index, column in enumerate(self.bit_columns[index]):
                # adds zeros or ones for each bit column
                if self.names[index][col_index] == value:
                    column.append(True)
                else:
                    column.append(False)

    def __repr__(self):
        return "BitmapIndex()"

    def __str__(self):
        res = ''
        for column_names in self.names:
            for value_name in column_names:
                res += value_name + '\t \t|'
            res += '|'
        res += '\n'
        for i in range(len(self.table)):
            for bitarrays in self.bit_columns:
                for arr in bitarrays:
                    res += str(int(arr[i])) + '\t \t|'
                res += '|'
            res += str(self.table[i])
            res += '\n'

        return res

    def _add_new_column_value(self, column_index, new_value):
        """
        Method to add bit column for new value
        """
        self.names[column_index].append(new_value)
        self.bit_columns[column_index].append(bitarray(len(self.bit_columns[column_index][0])))

    def _get_bitarr(self, column: int, key):
        """
        Returns bit representation of column by specified name
        """
        return (self.bit_columns[column])[self.names[column].index(key)]


def get_long_list_of_items():
    l = []
    i = 0
    for c_s in range(ord('A'), ord('z') + 1):
        for c_c in range(ord('A'), ord('z') + 1):
            for c_d in range(ord('0'), ord('9') + 1):
                for c_b in ['True', 'False', 'Maybe', 'None']:
                    l.append(Item(i, [chr(c_s), chr(c_c), chr(c_d), c_b]))
                    i += 1
    return l


def naive_search(l, item):
    ii = []
    for i, p in enumerate(l):
        if p.data == item.data:
            ii.append(i)
    return ii


if __name__ == '__main__':
    main()
