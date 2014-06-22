#!/usr/bin/env python
#coding=utf-8

import pdb
from models.bucket import Bucket 
from models.gentree import GenTree
from itertools import combinations


_DEBUG = True
gl_treelist = {}
gl_att_tree = {}
gl_treesupport = 0
gl_elementcount = 0
gl_result = []


# compare fuction for sort tree node
def node_cmp(node1, node2):
    """compare node1(str) and node2(str)
    Compare two nodes accroding to their support
    """
    support1 = gl_att_tree[node1].support
    support2 = gl_att_tree[node2].support
    if  support1 != support2:
        return cmp(support1, support2)
    else:
        return cmp(node1, node2)


def list_to_str(value_list, cmpfun=node_cmp, sep=';'):
    """covert sorted str list (sorted by cmpfun) to str 
    value (splited by sep). This fuction is value safe, which means 
    value_list will not be changed.
    """
    temp = value_list[:]
    temp.sort(cmp=cmpfun)
    return sep.join(temp)


def information_gain(bucket, pick_value=''):
    """get information gain from bucket accroding to pick_value
    """
    ig = 0.0
    parent_value = bucket.value
    cover_number = 0
    # Herein, all ncp will be divided by the same denominator.
    # So I don't computing true ncp, only use numerator part. 
    if pick_value == '':
        # compute bucket's information gain
        for gen_value in bucket.value:
            if gl_att_tree[gen_value].support == 0:
                continue
            for temp in bucket.member:
                ig = ig + trans_information_gain(temp, gen_value)
    else:
        # pick node's information gain
        if gl_att_tree[pick_value].support == 0:
            return 0
        for temp in bucket.member:
            ig = ig + trans_information_gain(temp, pick_value)
    return ig


def trans_information_gain(tran, pick_value):
    """get information gain for trans accroding to pick_value
    """
    ig = 0.0
    ncp = gl_att_tree[pick_value].support
    for t in tran:
        if pick_value in gl_treelist[t]:
            ig += ncp
    return ig


def pick_node(bucket):
    """find the split node with largest information gain. 
    Then split bucket to buckets accroding to this node.
    """
    buckets = {}
    result_list = []
    max_ig = -10000
    max_value = ''
    check_list = [t for t in bucket.value if t not in bucket.split_list]
    for t in check_list:
        if len(gl_att_tree[t].child) != 0:
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
    child_value = [t.value for t in gl_att_tree[max_value].child]
    for i in range(1, len(child_value)+1):
        temp = combinations(child_value, i)
        temp = [list(t) for t in temp]
        result_list.extend(temp)
    # generate child buckets
    child_level = bucket.level[:]
    child_value = bucket.value[:]
    now_level = bucket.level[index] + 1
    del child_level[index]
    del child_value[index]
    for temp in result_list:
        temp_level = child_level[:]
        temp_value = child_value[:]
        for t in temp:
            temp_level.insert(index, now_level)
            temp_value.insert(index, t)
        str_value = list_to_str(temp)
        buckets[str_value] = Bucket([], temp_value, temp_level)
    bucket.split_list.append(max_value)
    return (max_value, buckets)


def distribute_data(bucket, buckets, pick_value):
    """distribute records from parent_bucket to buckets (splited buckets)
    accroding to records elements.
    """
    if len(buckets) == 0:
        print "Error: buckets is empty!"
        return
    data = bucket.member[:]
    for temp in data:
        gen_list = []
        for t in temp:
            treelist = gl_treelist[t]
            try:
                pos = treelist.index(pick_value)
                # if covered, then replaced with new value
                if pos > 0:
                    gen_list.append(treelist[pos-1])
                else:
                    print "Error: pick node is leaf, which cannot be splited"
            except:
                continue
        gen_list = list(set(gen_list))
        # sort to ensure the order
        str_value = list_to_str(gen_list)
        try:
            buckets[str_value].member.append(temp)
        except:
            pdb.set_trace()
            print "Error: Cannot find key."


def balance_partitions(parent_bucket, buckets, K, pick_value):
    """handel buckets with less than K records
    """
    global gl_result
    left_over = []
    for k, t in buckets.items():
        if len(t.member) < K:
            # add records of buckets with less than K elemnts
            # to left_over partition
            left_over.extend(t.member[:])
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
        check_list = [t for t in buckets.values() if len(t.member) > K]
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
    if flag == False:
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
    """check if bucket can further drill down
    """
    if len(bucket.member) == K:
        bucket.splitable = False
        return False
    check_list = [t for t in bucket.value if t not in bucket.split_list]
    if bucket.splitable:
        for t in check_list:
            if len(gl_att_tree[t].child) != 0:
                return True
        bucket.splitable = False
    return False


def anonymize(bucket, K):
    """recursively split dataset to create anonymization buckets 
    """
    global gl_result
    if check_splitable(bucket, K) == False:
        gl_result.append(bucket)
        return
    (pick_value, expandNode) = pick_node(bucket)
    distribute_data(bucket, expandNode, pick_value)
    balance_partitions(bucket, expandNode, K, pick_value)
    for t in expandNode.values():
        anonymize(t, K)


def iloss(tran, middle):
    """return iloss caused by anon tran to middle
    """
    iloss = 0.0
    for t in tran:
        ntemp = gl_att_tree[t]
        checktemp = ntemp.parent[:]
        checktemp.insert(0, ntemp)
        for ptemp in checktemp:
            if ptemp.value in middle:
                break
        else:
            print "Program Error!!!! t=%s middle=%s" % (t, middle)
            pdb.set_trace()
        if ptemp.value == t:
            continue
        iloss = iloss + ptemp.support 
    # only one attribute is involved, so we can simplfy NCP
    iloss = iloss * 1.0 / gl_treesupport
    return iloss


def setalliloss(buckets):
    """return iloss sum of buckets, recompute iloss foreach bucket
    """
    alliloss = 0.0
    for gtemp in buckets:
        gloss = 0.0
        for mtemp in gtemp.member:
            gloss = gloss + iloss(mtemp, gtemp.value)
        gtemp.iloss = gloss
        alliloss += gloss
    alliloss = alliloss * 1.0 / gl_elementcount
    return alliloss


def partition(att_tree, data, K):
    """partition tran part of microdata
    """
    result = []
    global gl_treesupport, gl_treelist, gl_att_tree, gl_elementcount
    for t in data:
        gl_elementcount += len(t)
    gl_att_tree = att_tree
    gl_treesupport = gl_att_tree['*'].support
    for k, v in gl_att_tree.iteritems():
        if v.support == 0:
            gl_treelist[k] = [t.value for t in v.parent]
            gl_treelist[k].insert(0, k) 
    print '-'*30
    print "K=%d" % K
    anonymize(Bucket(data, ['*'], [0]), K)
    print "Publishing Result Data..."
    # changed to percentage
    all_loss = 100.0 * setalliloss(gl_result)
    if _DEBUG:
        print [len(t.member) for t in gl_result]
        print "Number of buckets %d" % len(gl_result)
        print '*' * 10
        print "iloss = %0.2f" % all_loss + "%"
    # transform result
    result = [t.member[:] for t in gl_result]
    return gl_result
