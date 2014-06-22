#!/usr/bin/env python
#coding=utf-8

# bucket for partition
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
        self.split_list = []
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