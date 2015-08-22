"""
run partition with given parameters
"""
#!/usr/bin/env python
# coding=utf-8
from partition_for_transaction import partition
from utils.read_data import read_data, read_tree
# from utils.make_tree import gen_even_BMS_tree
import sys
import copy
import random


def get_result_one(att_tree, data, k=10):
    """
    run partition for one time, with k=10
    """
    print "K=%d" % k
    _, eval_result = partition(att_tree, data, k)
    print "NCP %0.2f" % eval_result[0] + "%"
    print "Running time %0.2f" % eval_result[1] + " seconds"


def get_result_k(att_tree, data):
    """
    change k, whle fixing size of dataset
    """
    data_back = copy.deepcopy(data)
    # for k in range(5, 105, 5):
    for k in [2, 5, 10, 25, 50, 100]:
        print '#' * 30
        print "K=%d" % k
        result, eval_result = partition(att_tree, data, k)
        data = copy.deepcopy(data_back)
        print "NCP %0.2f" % eval_result[0] + "%"
        print "Running time %0.2f" % eval_result[1] + " seconds"


def get_result_dataset(att_tree, data, k=10, num_test=10):
    """
    fix k, while changing size of dataset
    num_test is the test nubmber.
    """
    data_back = copy.deepcopy(data)
    length = len(data_back)
    joint = 5000
    dataset_num = length / joint
    if length % joint == 0:
        dataset_num += 1
    for i in range(1, dataset_num + 1):
        pos = i * joint
        ncp = rtime = 0
        if pos > length:
            continue
        print '#' * 30
        print "size of dataset %d" % pos
        for j in range(num_test):
            temp = random.sample(data, pos)
            _, eval_result = partition(att_tree, temp, k)
            ncp += eval_result[0]
            rtime += eval_result[1]
            data = copy.deepcopy(data_back)
        ncp /= num_test
        rtime /= num_test
        print "Average NCP %0.2f" % ncp + "%"
        print "Running time %0.2f" % rtime + " seconds"
        print '#' * 30


if __name__ == '__main__':
    # set K=10 as default
    FLAG = ''
    DATA_SELECT = ''
    # gen_even_BMS_tree(5)
    try:
        DATA_SELECT = sys.argv[1]
        FLAG = sys.argv[2]
    except IndexError:
        pass
    INPUT_K = 10
    if DATA_SELECT == 'i':
        print "INFORMS data"
        DATA = read_data(1)
        ATT_TREE = read_tree(2)
    else:
        print "BMS-WebView data"
        DATA = read_data(0)
        ATT_TREE = read_tree(0)
    # read generalization hierarchy
    # read record
    # remove duplicate items
    for i in range(len(DATA)):
        DATA[i] = list(set(DATA[i]))
    print "Begin Partition"
    if FLAG == 'k':
        get_result_k(ATT_TREE, DATA)
    elif FLAG == 'data':
        get_result_dataset(ATT_TREE, DATA)
    elif FLAG == '':
        get_result_one(ATT_TREE, DATA)
    else:
        try:
            INPUT_K = int(FLAG)
            get_result_one(ATT_TREE, DATA, INPUT_K)
        except ValueError:
            print "Usage: python anonymizer [i | b] [k | data]"
            print "i: INFORMS ataset, b: BMS-WebView dataset"
            print "k: varying k"
            print "data: varying size of dataset"
            print "example: python anonymizer b 10"
            print "example: python anonymizer b k"
    # anonymized dataset is stored in result
    print "Finish Partition!!"
