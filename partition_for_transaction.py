#!/usr/bin/env python
#coding=utf-8

from generalization import Group, GenTree
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

def pick_node(group):
    groups = {}

    return groups

def distribute_data(trans, groups):
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



#fuctions for residue assignment and merge
def distance(value, middle):
    """return distance between two keys(groups)
    """
    temp = iloss(value, middle)
    return temp


def setalliloss(groups):
    """return iloss sum of groups, recompute iloss foreach group
    """
    alliloss = 0.0
    for k, gtemp in groups.iteritems():
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
    groups = {'*':Group(data,['*'],[0])}
    result = {}
    suppcount = 0
    suppress = {}
    print '-'*30
    print "K=%d" % K
    while groups:
        itemp = groups.popitem()
        gstemp = splitgroup(itemp[1])
        if len(gstemp) != 0:
            for k, gtemp in gstemp.iteritems():
                if len(gtemp.member) >= 2*K:
                    if k not in groups:
                        groups[k] = gtemp
                    else:
                        # todo
                        # pdb.set_trace()
                        groups[k] = merge_group(gtemp, ['*'])
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
        print "Group size %d" % len(result)
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
    
