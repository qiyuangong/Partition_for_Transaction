"""
main module of partition
"""
# The algorithm is proposed by Yeye He
# @Article{He2009,
#   Title = {Anonymization of set-valued data via top-down, local generalization},
#   Author = {He, Yeye and Naughton, Jeffrey F.},
#   Journal = {Proc. VLDB Endow.},
#   Year = {2009},
#   Month  = aug,
#   Number = {1},
#   Pages = {934--945},
#   Volume  = {2},
#   Acmid = {1687733},
#   ISSN = {2150-8097},
#   Issue_date = {August 2009},
#   Numpages = {12},
#   Publisher = {VLDB Endowment},
#   Url = {http://dl.acm.org/citation.cfm?id=1687627.1687733}
# }
# Implemented by Qiyuan Gong
# qiyuangong@gmail.com

# 2014-09-12

# !/usr/bin/env python
# coding=utf-8
import pdb
import time
from models.bucket import Bucket
from models.gentree import GenTree
from itertools import combinations


_DEBUG = False
PARENT_LIST = {}
ATT_TREE = {}
LEAF_NUM = 0
ELEMENT_NUM = 0
RESULT = []


# compare fuction for sort tree node
def node_cmp(node1, node2):
    """
    compare node1(str) and node2(str).
    Compare two nodes accroding to their leaf_num
    """
    support1 = len(ATT_TREE[node1])
    support2 = len(ATT_TREE[node2])
    if support1 != support2:
        return cmp(support1, support2)
    else:
        return cmp(node1, node2)


def list_to_str(value_list, cmpfun=node_cmp, sep=';'):
    """
    covert sorted str list (sorted by cmpfun) to str.
    value (splited by sep). This fuction is value safe, which means
    value_list will not be changed.
    """
    temp = value_list[:]
    temp.sort(cmp=cmpfun)
    return sep.join(temp)


def information_gain(bucket, pick_value):
    """
    get information gain from bucket accroding to pick_value.
    Information gain in this algorithm is different from its general meaning
    in information theory. It's one kind of distance fuction based on NCP for
    transaction.
    """
    ig = 0.0
    parent_value = bucket.value
    # Herein, all ncp will be divided by the same denominator.
    # So I don't computing true ncp, only use numerator part.
    # pick node's information gain
    if len(ATT_TREE[pick_value]) == 0:
        return 0
    for record in bucket.member:
        ig = ig + trans_information_gain(record, pick_value)
    return ig


def trans_information_gain(tran, pick_value):
    """
    get information gain for trans accroding to pick_value.
    In this algorithm, information gain is based on NCP for transaction.
    """
    ig = 0.0
    ncp = len(ATT_TREE[pick_value])
    for t in tran:
        if pick_value in set(PARENT_LIST[t]):
            ig += ncp
    return ig


def pick_node(bucket):
    """
    find the split node with largest information gain.
    Then split bucket to buckets accroding to this node.
    """
    buckets = {}
    result_list = []
    max_ig = -10000
    max_value = ''
    # if values in bucket have already be picked, it must have rolled back
    check_list = [t for t in bucket.value if t not in bucket.split_list]
    for t in check_list:
        if len(ATT_TREE[t].child) != 0:
            ig = information_gain(bucket, t)
            if ig > max_ig:
                max_ig = ig
                max_value = t
    # begin to expand node on pick_value
    if max_value == '':
        print "Error: list empty!!"
        return ('', {})
    # get index of max_value
    index = bucket.value.index(max_value)
    child_value = [t.value for t in ATT_TREE[max_value].child]
    for i in range(1, len(child_value) + 1):
        # For example, ALL->{A, B} can rilled down on {A},{B} and {A, B}
        # So, we need to compute all combinations for pick node
        temp = combinations(child_value, i)
        temp = [list(t) for t in temp]
        result_list.extend(temp)
    # generate child buckets
    child_value = bucket.value[:]
    del child_value[index]
    for temp in result_list:
        temp_value = child_value[:]
        for t in temp:
            temp_value.insert(index, t)
        str_value = list_to_str(temp)
        buckets[str_value] = Bucket([], temp_value)
    bucket.split_list.append(max_value)
    return (max_value, buckets)


def distribute_data(bucket, buckets, pick_value):
    """
    distribute records from parent_bucket to buckets (splited buckets)
    accroding to records elements.
    """
    if len(buckets) == 0:
        print "Error: buckets is empty!"
        return
    record_set = bucket.member[:]
    for record in record_set:
        gen_list = []
        for t in record:
            parent_list = PARENT_LIST[t]
            try:
                pos = parent_list.index(pick_value)
                # if covered, then replaced with new value
                if pos > 0:
                    gen_list.append(parent_list[pos - 1])
                else:
                    print "Error: pick node is leaf, which cannot be splited"
            except:
                continue
        gen_list = list(set(gen_list))
        # sort to ensure the order
        str_value = list_to_str(gen_list)
        try:
            buckets[str_value].member.append(record)
        except KeyError:
            pdb.set_trace()
            print "Error: Cannot find key."


def balance_partitions(parent_bucket, buckets, K, pick_value):
    """
    handel buckets with less than K records
    """
    global RESULT
    left_over = []
    for k, bucket in buckets.items():
        if len(bucket) < K:
            # add records of buckets with less than K elemnts
            # to left_over partition
            left_over.extend(bucket.member[:])
            del buckets[k]
    if len(left_over) == 0:
        # left over bucket is empty, skip balance step
        return
    # re-distribute transactions with least information gain from
    # buckets over k to left_over, to enshure number of
    # records in left_over is larger than K
    # using flag to denote if re-distribute is successful or not
    flag = True
    while len(left_over) < K:
        # each iterator pick least information gain transaction from buckets over K
        check_list = [t for t in buckets.values() if len(t) > K]
        if len(check_list) == 0:
            flag = False
            break
        min_ig = 10000000000000000
        min_key = (0, 0)
        for i, temp in enumerate(check_list):
            for j, t in enumerate(temp.member):
                ig = trans_information_gain(t, pick_value)
                if ig < min_ig:
                    min_ig = ig
                    min_key = (i, j)
        left_over.append(check_list[min_key[0]].member[min_key[1]][:])
        del check_list[min_key[0]].member[min_key[1]]
    if flag is False:
        # Note: if flag == False, means that split is unsuccessful.
        # So we need to pop a bucket from buckets to merge with left_over
        # The bucket poped is larger than K, so left over will larger than K
        parent_bucket.splitable = False
        try:
            min_ig = 10000000000000000
            min_key = ''
            for k, t in buckets.items():
                ig = information_gain(t, pick_value)
                if ig < min_ig:
                    min_ig = ig
                    min_key = k
            left_over.extend(buckets[min_key].member[:])
            del buckets[min_key]
        except:
            print "Error: buckets is empty"
            pdb.set_trace()
    parent_bucket.member = left_over[:]
    str_value = list_to_str(parent_bucket.value)
    buckets[str_value] = parent_bucket


def check_splitable(bucket, K):
    """
    check if bucket can further drill down.
    This fuction check all values have not been picked.
    """
    check_list = [t for t in bucket.value if t not in set(bucket.split_list)]
    if bucket.splitable:
        for t in check_list:
            if len(ATT_TREE[t].child) != 0:
                return True
        bucket.splitable = False
    return False


def anonymize(bucket, K):
    """recursively split dataset to create anonymization buckets
    """
    global RESULT
    if check_splitable(bucket, K) is False:
        RESULT.append(bucket)
        return
    (pick_value, expandNode) = pick_node(bucket)
    distribute_data(bucket, expandNode, pick_value)
    balance_partitions(bucket, expandNode, K, pick_value)
    for t in expandNode.values():
        anonymize(t, K)


def get_iloss(tran, middle):
    """
    return iloss caused by anon tran to middle
    """
    iloss = 0.0
    for t in tran:
        ntemp = ATT_TREE[t]
        checktemp = ntemp.parent[:]
        checktemp.insert(0, ntemp)
        for ptemp in checktemp:
            if ptemp.value in set(middle):
                break
        else:
            print "Program Error!!!! t=%s middle=%s" % (t, middle)
            pdb.set_trace()
        if ptemp.value == t:
            continue
        iloss = iloss + len(ptemp)
    # only one attribute is involved, so we can simplfy NCP
    iloss = iloss * 1.0 / LEAF_NUM
    return iloss


def init(att_tree, data, k):
    """
    init global variables
    """
    global LEAF_NUM, PARENT_LIST, ATT_TREE, ELEMENT_NUM, RESULT
    PARENT_LIST = {}
    RESULT = []
    LEAF_NUM = 0
    ELEMENT_NUM = 0
    for tran in data:
        ELEMENT_NUM += len(tran)
    ATT_TREE = att_tree
    LEAF_NUM = len(ATT_TREE['*'])
    for k, node in ATT_TREE.iteritems():
        if len(node) == 0:
            PARENT_LIST[k] = [t.value for t in node.parent]
            PARENT_LIST[k].insert(0, k)


def partition(att_tree, data, k):
    """
    partition tran part of microdata
    """
    init(att_tree, data, k)
    result = []
    # print '-' * 30
    start_time = time.time()
    anonymize(Bucket(data, ['*']), k)
    rtime = float(time.time() - start_time)
    # changed to percentage
    ncp = 0.0
    for partition in RESULT:
        pncp = 0.0
        for mtemp in partition.member:
            pncp = pncp + get_iloss(mtemp, partition.value)
            result.append(partition.value[:])
        partition.iloss = pncp
        ncp += pncp
    ncp = ncp * 100.0 / ELEMENT_NUM
    if _DEBUG:
        print "K=%d" % k
        print[len(t) for t in RESULT]
        print "Number of buckets %d" % len(RESULT)
        print '*' * 10
        print "ncp = %0.2f" % ncp + "%"
    # transform result
    return (result, (ncp, rtime))
