#!/usr/bin/env python
#coding=utf-8

from generalization import Bucket, GenTree
import random
import pdb
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
    # Herein, all ncp will be divided by the same denominator.
    # So I don't computing true ncp, only use numerator part. 
    if pick_value == '':
        for gen_value in bucket.value:
            ncp = 1.0 * gl_att_tree[gen_value].support
            cover_number = 0
            for temp in bucket.member:
                for t in temp:
                    if gen_value in gl_treelist[t]:
                        cover_number += 1
            ig += ncp * cover_number
    else:
        # compute bucket's information gain
        ncp = 1.0 * gl_att_tree[pick_value].support
        for temp in bucket.member:
            for t in temp:
                if pick_value in gl_treelist[t]:
                    ig += ncp
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
    # begin to expand node on pick_value
    if max_value != '':
        index = bucket.value.index(max_value)
        child_value = [t.value for t in gl_att_tree[max_value].child]
        for i in range(1, len(child_value)+1):
            temp = combinations(child_value, i)
            temp = [list(t) for t in temp]
            result_list.extend(temp)
        # generate chlid buckets
        for temp in result_list:
            child_level = bucket.level[:]
            child_value = bucket.value[:]
            now_level = bucket.level[index] + 1
            del child_level[index]
            del child_value[index]
            for t in temp:
                child_level.insert(index, now_level)
                child_value.insert(index, t)
            hash_value = child_value[:]
            hash_value.sort()
            str_value = ';'.join(hash_value)
            buckets[str_value] = Bucket([], child_value, child_level)
    return (max_value, buckets)


def distribute_data(bucket, buckets, pick_value):
    """distribute records from parent_bucket to buckets (splited buckets)
    accroding to records elements.
    """
    if len(buckets) == 0:
        return
    data = bucket.member[:]
    parent_level = bucket.level[:]
    parent_value = bucket.value[:]
    for temp in data:
        gen_list = []
        for t in temp:
            treelist = gl_treelist[t]
            try:
                pos = treelist.index(pick_value)
                # if covered, then replaced with new value
                gen_list.append(treelist[pos-1])
            except:
                # todo uncovered eleements
                gen_value = ''
                for t in parent_level:
                    if t > len(treelist):
                        continue
                    gen_value = treelist[-1-t]
                    if gen_value in parent_value:
                        gen_list.append(gen_value)
                        break
        gen_list = list(set(gen_list))
        # sort to ensure the order
        gen_list.sort()
        str_value = ';'.join(gen_list)
        try:
            buckets[str_value].member.append(temp)
        except:
            pdb.set_trace()
            print "ERROR: Cannot find key."
    # pdb.set_trace()


def balance_partitions(parent_bucket, buckets, K):
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
            left_over.extend(min_bucket.member[:])
        except:
            pdb.set_trace()
        del buckets[min_key]
    if len(left_over):  
        parent_bucket.member = left_over[:]
        gl_result.append(parent_bucket)


def check_splitable(bucket):
    """check if bucket can further drill down
    """
    if bucket.splitable:
        for t in bucket.value:
            if len(gl_att_tree[t].child) != 0:
                return True
        bucket.splitable = False
    return False


def anonymize(bucket, K):
    """recursively split dataset to create anonymization buckets 
    """
    global gl_result
    if check_splitable(bucket) == False:
        gl_result.append(bucket)
        return
    (pick_value, expandNode) = pick_node(bucket)
    distribute_data(bucket, expandNode, pick_value)
    balance_partitions(bucket, expandNode, K)
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


def partition(K, att_tree, data):
    """partition tran part of microdata
    """
    global gl_treesupport, gl_treelist, gl_att_tree, gl_elementcount
    for t in data:
        gl_elementcount += len(t)
    gl_att_tree = att_tree
    gl_treesupport = gl_att_tree['*'].support
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
    # changed to percentage
    all_loss = 100.0 * setalliloss(gl_result)
    # pdb.set_trace()
    if _DEBUG:
        print [len(t.member) for t in gl_result]
        print "Number of buckets %d" % len(gl_result)
        print '*' * 10
        print "iloss = %0.2f" % all_loss + "%"
    return gl_result
