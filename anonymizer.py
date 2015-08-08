#!/usr/bin/env python
# coding=utf-8
from partition_for_transaction import partition
from utils.read_data import read_data, read_tree
from utils.save_result import save_to_file
import sys


if __name__ == '__main__':
    # set K=10 as default
    K = 10
    try:
        K = int(sys.argv[1])
    except:
        pass
    # read generalization hierarchy
    ATT_TREES = read_tree()
    # read record
    TRANSACTIONS = read_data()
    # remove duplicate items
    for i in range(len(TRANSACTIONS)):
        TRANSACTIONS[i] = list(set(TRANSACTIONS[i]))
    print "Begin Partition"
    result = partition(ATT_TREES, TRANSACTIONS, K)
    # save_to_file(result)
    print "Finish Partition!!"
