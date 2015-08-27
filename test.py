import unittest
import pdb
from partition_for_transaction import partition, list_to_str
from models.gentree import GenTree

# Build a GenTree object
ATT_TREE = {}


def init_tree():
    global ATT_TREE
    ATT_TREE = {}
    root = GenTree('*')
    ATT_TREE['*'] = root
    lt = GenTree('A', root)
    ATT_TREE['A'] = lt
    ATT_TREE['a1'] = GenTree('a1', lt, True)
    ATT_TREE['a2'] = GenTree('a2', lt, True)
    rt = GenTree('B', root)
    ATT_TREE['B'] = rt
    ATT_TREE['b1'] = GenTree('b1', rt, True)
    ATT_TREE['b2'] = GenTree('b2', rt, True)


class test_partition(unittest.TestCase):
    def test_case_from_paper(self):
        init_tree()
        trans = [['a1'],
                 ['a1', 'a2'],
                 ['b1', 'b2'],
                 ['b1', 'b2'],
                 ['a1', 'a2', 'b2'],
                 ['a1', 'a2', 'b2'],
                 ['a1', 'a2', 'b1', 'b2']]
        result, _ = partition(ATT_TREE, trans, 2)
        for i, t in enumerate(result[:]):
            result[i] = list_to_str(t)
        self.assertEqual(set(result),
                         set(['A', 'A', 'a1;a2;B', 'a1;a2;B', 'a1;a2;B', 'b1;b2', 'b1;b2']))

if __name__ == '__main__':
    unittest.main()
