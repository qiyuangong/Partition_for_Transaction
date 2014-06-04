#!/usr/bin/env python
#coding=utf-8

# logic tree
class GenTree(object):

    """Class for Generalization hierarchies (Taxonomy Tree). 
    Store tree node in instances.
    self.value: node value
    self.level: tree level (top is 0)
    self.support: support
    self.parent: ancestor node list
    self.child: successor node list
    self.cover: leaf values cover by node
    """

    def __init__(self, value = None, parent = None):
        self.value = ''
        self.level = 0
        self.support = 0
        self.parent = []
        self.child = []
        # range is for ARE, all possible values are in range
        self.cover = {}
        if value != None:
            self.value = value
        if parent != None:
            self.parent = parent.parent[:]
            self.parent.insert(0, parent)
            parent.child.append(self)
            self.level = parent.level + 1
            for t in self.parent:
                t.support += 1
                t.cover[self.value] = self
                
    def node(self, value):
        """Search tree with value, return GenTree node.
        If value == node value, return node. 
        If value != node value, recurse search.
        """
        return self.cover[value]


class Bucket:

    """Class for Group, which is used to keep records 
    Store tree node in instances.
    self.iloss: information loss of the whole group
    self.member: records in group
    self.value: group value
    self.level: tree level (top is 0)
    """

    def __init__(self, data, value = ['*'], level = []):
        self.iloss = 0.0
        self.member = data
        self.value = value[:]
        self.level = level[:]
        self.leftover = []
        self.splitable = True

    def merge_group(self, guest, middle):
        "merge guest into hostgourp"
        while guest.member:
            temp = guest.member.pop()
            self.member.append(temp)
        self.value = middle[:]

    def merge_record(self, rtemp, middle):
        "merge record into hostgourp"
        self.member.append(rtemp)
        self.value = middle[:]