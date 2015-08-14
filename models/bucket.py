"""
bucket class
"""
#!/usr/bin/env python
# coding=utf-8

# bucket for partition


class Bucket:

    """Class for Group, which is used to keep records
    Store tree node in instances.
    self.iloss: information loss of the whole group
    self.split_list: record values picked (used for revert)
    self.member: records in group
    self.value: group value, generalization result for all members in SA
    self.splitable: True (False) means that group can (not) be split
    """

    def __init__(self, data, value=['*']):
        self.iloss = 0.0
        self.split_list = []
        self.member = data
        self.value = value[:]
        self.splitable = True

    def __len__(self):
        """
        return the number of records in bucket
        """
        return len(self.member)
