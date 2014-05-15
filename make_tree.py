#!/usr/bin/env python
#coding=utf-8
import string
import math

#generate tree from treeseed
def gen_ICD9CODX_tree():
    """This generalization hierarchy is defined according to ICD9 code hierarchy.
    """
    # disease tree is more complex, so we need treeseed to simplify definition
    treeseed = open('data/treeseed_ICD9CODX.txt','rU')
    treefile = open('data/treefile_ICD9CODX.txt','w')

    for line in treeseed:
        # get low bound tree leaf
        title = '' 
        temp = line.split(';')
        #separate special value
        if temp[0][0] != 'E' and temp[0][0] != 'V':
            now = string.atoi(temp[0])
            bottom = string.atoi(temp[1].split(',')[0])
            top = string.atoi(temp[1].split(',')[1])
            if now > bottom:
                treefile.write(line)
                continue    
            index = line.find(';')
            while bottom <= top:
                stemp = str(bottom)
                if bottom < 100 and bottom >= 0:
                    stemp = '0' + stemp
                if bottom < 10 and bottom >= 0:
                    stemp = '0' + stemp
                treefile.write(stemp + line[index:])
                bottom = bottom + 1
        else:
            title = temp[0][0]
            now = string.atoi(temp[0][1:])
            bottom = string.atoi(temp[1].split(',')[0][1:])
            top = string.atoi(temp[1].split(',')[1][1:])
            if now > bottom:
                treefile.write(line)
                continue    
            index = line.find(';')
            while bottom <= top:
                stemp = str(bottom)
                if bottom < 10:
                    stemp = '0' + stemp
                treefile.write(title + stemp + line[index:])
                bottom = bottom + 1
    treeseed.close()
    treefile.close()


def gen_even_tree(fanout):
    """This generalization hierarchy is defined according to even fan-out (average distribution).
    For large dataset fanout = 5, for small dataset fanout = 4
    """
    treeseed = open('data/treeseed_even.txt','rU')
    treefile = open('data/treefile_even.txt','w')

    for line in treeseed:
        line = line.strip()
        temp = line.split(',')
        prefix = ''
        str_len = len(temp[0])
        if temp[0][0] == 'E' or temp[0][0] == 'V':
            prefix = temp[0][0]
            temp[0] = temp[0][1:]
            temp[1] = temp[1][1:]
            str_len -= 1
        bottom = string.atoi(temp[0])
        top = string.atoi(temp[1])
        # get height
        temp = top - bottom
        height = 0
        flag = True
        while temp:
            temp /= fanout
            height += 1
        level_len = []
        tree = []
        for i in range(height):
            level_len = pow(fanout, i)
            level_split = []
            temp = bottom
            while temp <= top:
                stemp = ''
                if level_len == 1:
                    stemp = prefix+str(temp).rjust(str_len, '0')
                elif temp+level_len-1 > top:
                    stemp = prefix+str(temp).rjust(str_len, '0')
                    stemp += ','+ prefix+str(top).rjust(str_len, '0')
                else:
                    stemp = prefix+str(temp).rjust(str_len, '0')
                    stemp += ','+ prefix+str(temp+level_len-1).rjust(str_len, '0')
                level_split.append(stemp)
                temp += level_len
            tree.append(level_split)
        for i in range(len(tree[0])):
            w_line = ''
            temp = i
            for index in range(height):
                w_line += tree[index][temp] + ';'
                temp /= fanout
            w_line += line + ';*\n'
            treefile.write(w_line)
    treeseed.close()
    treefile.close()

if __name__ == '__main__':
    # gen_ICD9CODX_tree()
    # gen_even_tree(5)    
