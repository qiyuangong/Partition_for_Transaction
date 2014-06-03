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
        ncp = 1.0 *  / len(gl_att_tree(parent_value).child)
        for temp in bucket.member:
            for t in temp:
                if parent_value in gl_treelist(t):
                ig += ncp * len(gl_att_tree(t).child)
    else:
        # Herein, all ncp will be divided by the same denominator.
        # So I don't computing true ncp, only use numerator part. 
        ncp = 1.0 * len(gl_att_tree(pick_value).child) / \
            len(gl_att_tree(parent_value).child)
        for temp in bucket.member:
            for t in temp:
                if pick_value in gl_treelist(t):
                    cover_number += 1
        ig = ncp * cover_number
    return ig


def pick_node(bucket):
    """find the split node with largest information gain. 
    Then split bucket to buckets accroding to this node.
    """
    valuelist = []
    max_ig = 100000000000
    max_value = ''
    buckets = {}
    for t in bucket.value:
        if len(gl_att_tree(t).child) != 0:
            ig = information_gain(bucket, t)
            if ig > max_ig:
                ig = max_ig
                max_value = t
    # begin to expand node on pick_value
    if max_value != '':
        child_value = [t.value for t in gl_att_tree(max_value).child]
        result_list = combinations(child_value)
        result_list = list(set(result_list))
        # todo: check the result
        for t in result_list:
            t.sort(cmp=node_cmp,reverse=True)
            str_value = ''.join(t)
            buckets[str_value] = Bucket([], t, bucket.level+1))
    return buckets


def distribute_data(parent_bucket, buckets):
    """distribute records from parent_bucket to buckets (splited buckets)
    accroding to records elements.
    """
    data = parent_bucket.data[:]
    parent_value = parent_bucket.value
    parent_level = parent_bucket.level
    for temp in data:
        cover_list = []
        for t in temp:
            if parent_value in gl_treelist(t):
                cover_list.append(gl_treelist(t)[-1 *(parent_level+2)])
        # sort to ensure the order
        cover_list.sort(cmp=node_cmp,reverse=True)
        str_value = ''.join(cover_list)
        try:
            buckets[str_value].member.append()
        except:
            print "ERROR: Cannot find key."
    return buckets


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
        left_over.expand(min_bucket.member)
        del buckets[min_key]
    parent_bucket.member = left_over[:]


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
    buckets = {'*':Bucket(data,['*'],[0])}
    result = {}
    suppcount = 0
    suppress = {}
    print '-'*30
    print "K=%d" % K
    while buckets:
        itemp = buckets.popitem()
        gstemp = splitgroup(itemp[1])
        if len(gstemp) != 0:
            for k, gtemp in gstemp.iteritems():
                if len(gtemp.member) >= 2*K:
                    if k not in buckets:
                        buckets[k] = gtemp
                    else:
                        # todo
                        # pdb.set_trace()
                        buckets[k] = merge_group(gtemp, ['*'])
                elif len(gtemp.member) < K:
                    suppcount = suppcount + 1
                    suppress[k] = gtemp
                else:
                    result[k] = gtemp
        else:
            if _DEBUG:
                print itemp[0] + " cannot be split" 
            result[itemp[0]] = itemp[1]
    print "Publishing Result Data..."
    # set and get iloss
    loss = setalliloss(result)
    if _DEBUG:
        print "Number of buckets %d" % len(result)
        print "resultcount = %d" % len(result)
        print '*' * 10
        print "iloss = %d" % loss
        print "suppress = %s" % suppcount
        print "Residue assigment..."
    rassignment(suppress, result)
    # get iloss
    loss = setalliloss(result)
    print "iloss = %d" % loss
    print "suppress = %s" % len(suppress)
    return result
    
