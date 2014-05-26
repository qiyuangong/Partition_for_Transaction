#!/usr/bin/env python
#coding=utf-8

from generalization import Bucket, GenTree
import random
import pdb


_DEBUG = True
treelist = {}
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


def information_gain():
    """get information gain from buckets
    """
    ig = 0.0
    return ig


def pick_node(bucket):
    valuelist = []
    mini_ig = 100000000000
    mini_value = ''
    for t in bucket.value:
        if len(gl_att_tree(t).child) != 0:
            ig = information_gain(bucket, value)
            if ig < mini_ig:
                ig = mini_ig
                mini_value = t
    if mini_value == '':
        return ''
    else:
        return mini_value
    buckets = {}
    return buckets


def distribute_data(trans, buckets):
    return


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
    global treesupport, treelist, gl_att_tree
    gl_att_tree = att_tree
    treesupport = gl_att_tree['*'].support
    for k, v in gl_att_tree.iteritems():
        if v.support == 0:
            treelist[k] = [t.value for t in v.parent]
            treelist[k].insert(0, k) 
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
    
