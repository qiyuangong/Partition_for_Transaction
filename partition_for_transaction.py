#!/usr/bin/env python
#coding=utf-8

from generalization import Bucket, GenTree
import random
import pdb
from itertools import combinations


_DEBUG = True
gl_treelist = {}
gl_att_tree = {}
treesupport = 0
gl_result = []

# compare fuction for sort tree node
def node_cmp(node1, node2):
    """compare node1(str) and node2(str)
    Compare two nodes accroding to their support
    """
    global gl_att_tree
    support1 = gl_att_tree[node1].support
    support2 = gl_att_tree[node2].support
    if  support1 != support2:
        return support1 - support2
    else:
        return (node1 > node2)


def information_gain(bucket, pick_value=''):
    """get information gain from bucket accroding to pick_value
    """
    ig = 0.0
    parent_value = bucket.value
    cover_number = 0
    if pick_value == '':
        # compute bucket's information gain
        ncp = 1.0 
        for temp in bucket.member:
            for t in temp:
                if pick_value in gl_treelist[t]:
                    ig += ncp * len(gl_att_tree[t].child)
    else:
        # Herein, all ncp will be divided by the same denominator.
        # So I don't computing true ncp, only use numerator part. 
        ncp = 1.0 * len(gl_att_tree[pick_value].child) 
        for temp in bucket.member:
            for t in temp:
                if pick_value in gl_treelist[t]:
                    cover_number += 1
        ig = ncp * cover_number
    return ig


def pick_node(bucket):
    """find the split node with largest information gain. 
    Then split bucket to buckets accroding to this node.
    """
    valuelist = []
    max_ig = -10000
    max_value = ''
    buckets = {}
    result_list = []
    for t in bucket.value:
        if len(gl_att_tree[t].child) != 0:
            ig = information_gain(bucket, t)
            if ig > max_ig:
                ig = max_ig
                max_value = t
    index = bucket.value.index(max_value)
    # begin to expand node on pick_value
    if max_value != '':
        child_value = [t.value for t in gl_att_tree[max_value].child]
        for i in range(2, len(child_value)):
            temp = combinations(child_value, i)
            result_list.extend(list(set(temp)))
        # todo: check the result
        for t in result_list:
            t = list(t)
            t.sort()
        result_list.extend(child_value)
        # generate chlid buckets
        for temp in result_list:
            child_level = bucket.level[:]
            child_value = bucket.value[:]
            now_level = bucket.level[index]
            del child_level[index]
            del child_value[index]
            for t in temp:
                child_level.insert(index, now_level)
                child_value.insert(index, t)
            str_value = ';'.join(child_value)
            buckets[str_value] = Bucket([], child_value, child_level)
    return buckets


def distribute_data(parent_bucket, buckets):
    """distribute records from parent_bucket to buckets (splited buckets)
    accroding to records elements.
    """
    if len(buckets) == 0:
        return
    data = parent_bucket.member[:]
    parent_value = parent_bucket.value
    parent_level = parent_bucket.level
    for temp in data:
        cover_list = []
        for t in temp:
            if parent_value in gl_treelist[t]:
                cover_list.append(gl_treelist[t][-1 *(parent_level+2)])
        # sort to ensure the order
        cover_list.sort()
        # str_value = ';'.join(cover_list)
        str_value =
        try:
            buckets[str_value].member.append()
        except:
            pdb.set_trace()
            print "ERROR: Cannot find key."
    # return buckets


def balance_partitions(parent_bucket, buckets, K):
    """handel buckets with less than K records
    """
    left_over = []
    for k, t in buckets.iteritems():
        if len(t.member) < K:
            # add records of buckets with less than K elemnts
            # to left_over partition
            left_over.expand(t.member)
            del buckets[k]
    if len(left_over) < K:
        # re-distribute bucket with least information gain to left_over
        # to enshure number of records in left_over is larger than K
        min_ig = 10000000000000000
        min_bucket = None
        min_key = ''
        for k, t in buckets.iteritems():
            ig = information_gain(t)
            if ig < min_ig:
                min_ig = ig
                min_bucket = t
                min_key = k
        if min_key == '':
            return
        try:
            left_over.extend(min_bucket.member)
        except:
            pdb.set_trace()
        del buckets[min_key]
    parent_bucket.member = left_over[:]
    if len(buckets) == 0:
        parent_bucket.splitable = False


def iloss(tran, middle):
    """return iloss caused by anon tran to middle
    """
    iloss = 0.0
    for t in tran:
        ntemp = gl_att_tree[t]
        checktemp = ntemp.parent[:]
        checktemp.insert(0, ntemp)
        for i, ptemp in enumerate(checktemp):
            if ptemp.value in middle:
                break
        else:
            print "Program Error!!!! t=%s middle=%s" % (t, middle)
            pdb.set_trace()
        if ptemp.value == t:
            continue
        iloss = iloss + ptemp.support * 1.0 / treesupport
    return iloss


def setalliloss(buckets):
    """return iloss sum of buckets, recompute iloss foreach bucket
    """
    alliloss = 0.0
    for k, gtemp in buckets.iteritems():
        gloss = 0.0
        for mtemp in gtemp.member:
            gloss = gloss + iloss(mtemp, gtemp.value)
        gtemp.iloss = gloss
        alliloss += gloss
    return alliloss


def partition(K, att_tree, data):
    """partition tran part of microdata
    """
    global treesupport, gl_treelist, gl_att_tree
    gl_att_tree = att_tree
    treesupport = gl_att_tree['*'].support
    for k, v in gl_att_tree.iteritems():
        if v.support == 0:
            gl_treelist[k] = [t.value for t in v.parent]
            gl_treelist[k].insert(0, k) 
    # bucket = {'*':Bucket(data,['*'],[0])}
    result = {}
    suppcount = 0
    suppress = {}
    print '-'*30
    print "K=%d" % K

    anonymize(Bucket(data,['*'],[0]), K)

    print "Publishing Result Data..."
    # set and get iloss
    # todo 
    # loss = setalliloss(result)
    # if _DEBUG:
    #     print "Number of buckets %d" % len(result)
    #     print "resultcount = %d" % len(result)
    #     print '*' * 10
    #     print "iloss = %d" % loss
    #     print "suppress = %s" % suppcount
    #     print "Residue assigment..."
    # rassignment(suppress, result)
    # # get iloss
    # loss = setalliloss(result)
    # print "iloss = %d" % loss
    # print "suppress = %s" % len(suppress)
    # return result


def anonymize(bucket, K):
    if bucket.splitable == False:
        gl_result.append(bucket)
        return
    expandNode = pick_node(bucket)
    distribute_data(bucket, expandNode)
    balance_partitions(bucket, expandNode, K)
    for t in expandNode.keys():
        anonymize(t, K)

    
    
