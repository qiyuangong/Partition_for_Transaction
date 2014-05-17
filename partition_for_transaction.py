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


def belong(tran, value, level):
    """return tran's gen cut
    value denote generalization cut, 
    """
    ltemp = []
    result = ''
    for t in tran:
        # make sure t in chlid of v
        if value not in treelist[t]:
            continue
        lentran = len(treelist[t])
        v = treelist[t][lentran - level - 1]
        ltemp.append(v)
    # remove duplicate elements
    ltemp = list(set(ltemp))
    ltemp.sort()
    result = ';'.join(ltemp)
    return result 


def splitgroup(group):
    """try to split group.
    if group can be splited, return splited groups
    else return {}
    """
    if _DEBUG:
        print 'Begin to split %s' % group.value
    member = group.member
    value = group.value
    level = group.level
    groups = {}
    # todo
    for t in value:
        if len(gl_att_tree[t].child) != 0:
            break
    else:
        return groups
    index = value.index(t)
    tlevel = level[index] + 1
    while member:
        temp = member.pop()
        vsplit = belong(temp, value[index], tlevel)
        if vsplit == '':
            pdb.set_trace()
        gvalue = value[:]
        glevel = level[:]
        vtemp = vsplit.split(';')
        del gvalue[index]
        del glevel[index]
        for t in vtemp:
            if t != '':
                gvalue.insert(index,t)
                glevel.insert(index,tlevel)
        if _DEBUG:
            print 'parent=%s' % gvalue
        v = ';'.join(gvalue)
        if not v in groups:
            groups[v] = Group([temp], gvalue, glevel)
        else:
            groups[v].member.append(temp)
    return groups


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


def middle(tran1, tran2):
    """return gen result of two tran1
    """
    treemark1 = {}
    treemark2 = {}
    trantemp = []
    alltran = tran1[:]
    alltran.extend(tran2)
    # mark the gen tree with red color
    for t in tran1:
        treemark1[t] = 1
        ptemp = gl_att_tree[t].parent
        for pt in ptemp:
            if not pt.value in treemark1:
                treemark1[pt.value] = 1
            else:
                treemark1[pt.value] += 1
    # check the other color
    for t in tran2:
        if treemark1.has_key(t):
            if not t in trantemp:
                trantemp.append(t)
        treemark2[t] = 1
        ptemp = gl_att_tree[t].parent
        for pt in ptemp:
            if not pt.value in treemark2:
                treemark2[pt.value] = 1
            else:
                treemark2[pt.value] += 1
            if treemark1.has_key(pt.value):
                if not pt.value in trantemp:
                    trantemp.append(pt.value)
    if len(trantemp) <= 1:
        return trantemp
    trantemp.sort(cmp=node_cmp, reverse=True)
    dellist = []
    for t in trantemp:
        ptemp = gl_att_tree[t].child
        checklist = []
        for pt in ptemp:
            if pt.value in trantemp:
                checklist.append(pt.value)
        if t in dellist:
            for pt in checklist:
                dellist.append(pt)
            continue
        sum1 = 0
        sum2 = 0
        for pt in checklist:
            sum1 += treemark1[pt]
            sum2 += treemark2[pt]
        if sum1 == treemark1[t] and sum2 == treemark2[t]:
            dellist.append(t)
        else:
            for pt in checklist:
                dellist.append(pt)
    for t in dellist:
        try:
            trantemp.remove(t)
        except:
            print "Error!! When del value according to dellist "
            pdb.set_trace()
    return trantemp


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
        gtemp.gloss = gloss
        alliloss += gloss
    return alliloss


def rassignment(suppress, result):
    """residue assigment step. 
    """
    #merge with themselves
    while suppress:
        temp = suppress.popitem()
        mindis = 10000000000
        minindex = ''
        minmiddle = ['*']
        for k, v in result.iteritems():
            mtemp = middle(temp[1].value, v.value)
            dtemp = len(temp[1].member) * distance(temp[1].value, mtemp) + len(v.member) * distance(v.value, mtemp)
            if dtemp < mindis:
                mindis = dtemp
                minindex = k
                minmiddle = mtemp
        result[minindex].merge_group(temp[1], minmiddle)
    # update group middle
    for k, v in result.iteritems():
        temp = ';'.join(v.value)
        result[temp] = result.pop(k)
    return 


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
    