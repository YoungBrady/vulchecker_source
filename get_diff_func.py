# -- coding: utf-8 --
from access_db_operate import *
from complete_PDG import *
import re
from py2neo.packages.httpstream import http
http.socket_timeout = 9999999
import sys
import pickle
# args=sys.argv
# filetype=args[1]

def get_cfg_relation():
    j = JoernSteps()
    j.connectToDatabase()
    all_func_node = getALLFuncNode(j)

    len1=len(all_func_node)
    # print('all_func_node',all_func_node)
    for node in all_func_node:

        filepath = getFuncFile(j, node._id)
        filename=filepath.split('/')[-1][-2]##去掉.c
        cwe=filepath.split('/')[-3]
        type=filepath.split('/')[-4]
# def get_diff_lines()       

if __name__ == "__main__":
    args=sys.argv
    filetype=args[1]
    difffile=f'cwe2file2linenum_{filetype}.pkl'
    f=open(difffile,'rb')
    cwe2file2linenum=pickle.load(f)
    f.close()
    get_cfg_relation()

