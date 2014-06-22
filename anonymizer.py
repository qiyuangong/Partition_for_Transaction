#!/usr/bin/env python
#coding=utf-8
from partition_for_transaction import partition
from utils.read_data import read_data, read_tree
from utils.evaluation import average_relative_error
from utils.save_result import save_to_file
import sys
# Poulis set k=25, m=2 as default!

if __name__ == '__main__':
    K = 10
    try:
        K = int(sys.argv[1])
    except:
        pass
    #read gentree tax
    att_tree = read_tree()
    #read record
    trans = read_data()
    # remove duplicate items
    for i in range(len(trans)):
        trans[i] = list(set(trans[i]))
    print "Begin Partition"
    result = partition(att_tree, trans, K)
    # save_to_file(result)
    print "Finish Partition!!"
    # print "Begin Evaluation"
    # are = average_relative_error(att_tree, trans, result)
    # print "Average Relative Error: %.2f" % are
