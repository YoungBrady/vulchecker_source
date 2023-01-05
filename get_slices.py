# coding:utf-8
from __future__ import print_function
from joern.all import JoernSteps
from igraph import *
from access_db_operate import *
from slice_op import *
from py2neo.packages.httpstream import http
from optparse import OptionParser
import copy
http.socket_timeout = 9999
import sys



def get_ast_parent_code(nodeid,j):
    query_str="g.v(%s).in('IS_AST_PARENT').code"%nodeid
    code = j.runGremlinQuery(query_str)
    # print('code:',code)
    return code[0]

def get_func_def_code(nodeid,j):
    query_str="g.v(%s).out('IS_FUNCTION_OF_AST').code"%nodeid
    code = j.runGremlinQuery(query_str)
    # print('code:',code)
    return code[0]

def get_slice_file_sequence(slice_store_filepath, edges_store_filepath, list_result, list_edge, cnt, func_name, startline1, filepath_all, var_list):

    index = 0
    point_var_list = []
    list_write2file = []
    list_edge2file = []
    list_index2node = []
    id2index={}
    vulfunc_id = list_result[0]['functionId']  # 第一句肯定是漏洞函数的开头
      
    # list_result=sortedNodesByLoc(set(list_result))
    # if len(list_result)<10:
    #     return
    for node in list_result:
        index += 1
        raw = int(node['location'].split(':')[0])-1
        file_name = ('/').join(node['filepath'].split('/')[-3:])
        list_write2file.append(node['code'] + ' location: ' + str(raw+1) + ' file: ' + file_name +' type: ' + node['type']+' id: ' + node['name']+ '\n')

        # list_index2node.append((index, node['name']))
        id2index[node['name']]=index

        # if node['type'] == 'Parameter':
        #     if((node['functionId'] == vulfunc_id) and ('* ' in node['code'])):  # 保存指针类型的变量
        #         pit_var = node['code'].split('* ')[-1].strip()  # int ff_hevc_decode_nal_sps(HEVCContext *s)
        #         if(pit_var[-1] == ','):
        #             pit_var = pit_var[:-1]
        #         elif(pit_var[-1] == ')'):
        #             pit_var = pit_var[:-1]
        #         point_var_list.append(pit_var)

        # if node['type'] == 'IdentifierDeclStatement':
        #     if((node['functionId'] == vulfunc_id) and ('* ' in node['code'])):  # 保存指针类型的变量
        #         # BoxBlurContext * s = ctx->priv;    BoxBlurContext * s, linesize    BoxBlurContext * s, * linesize
        #         ass_var = node['code'].split(' = ')
        #         if(len(ass_var) > 1):
        #             end = len(ass_var) - 1
        #         else:
        #             end = len(ass_var)
        #         for i in range(end):  # 考虑连等的情况
        #             pit_var = ass_var[i].split('* ')
        #             for j in range(1, len(pit_var)):
        #                 tmp_var = pit_var[j].strip()
        #                 if tmp_var == '':
        #                     continue
        #                 if((tmp_var[-1] == ',') or (tmp_var[-1] == ';')):
        #                     point_var_list.append(tmp_var[:-1].strip())
        #                 else:
        #                     point_var_list.append(tmp_var.strip())

    for edge in list_edge:
        # flag1 = 0
        # flag2 = 0
        # # print(edge)
        # for tuple in list_index2node:
        #     if edge[0] == tuple[1]:
        #         start_index = tuple[0]
        #         flag1 = 1

        #     if edge[1] == tuple[1]:
        #         target_index = tuple[0]
        #         flag2 = 1

        # if flag1 and flag2 and (start_index, target_index) not in list_edge2file:
        #     tuple = (start_index, target_index)
        #     list_edge2file.append(tuple)
        if edge[0] in id2index and edge[1] in id2index:
            a=id2index[edge[0]]
            b=id2index[edge[1]]
            if a>len(list_result) or b>len(list_result):
                print(slice_store_filepath)
            list_edge2file.append((id2index[edge[0]],id2index[edge[1]]))
        # else:
            # print(edge)

    sorted_edges = sorted(list_edge2file, key=lambda t: (t[0], t[1]))

    f = open(slice_store_filepath, 'a')
    # f.write(str(cnt) + ' @@ ' + filepath_all + ' @@ ' + func_name + ' @@ ' + startline1 + ',' + startline2 + ' @@ ' + str(var_list) + ' @@ ' + '{')
    f.write(str(cnt) + ' @@ ' + filepath_all + ' @@ ' + func_name + ' @@ ' + startline1 + ' @@ ' + str(var_list)+'\n')
    # for i in point_var_list:
    #     if(i == point_var_list[-1]):  # 最后一个不用写入‘, ’
    #         f.write(str(i))
    #     else:
    #         f.write(str(i) + ', ')
    # f.write('}' + '\n')

    for wb in list_write2file:
        f.write(wb)
    f.write('------------------------------' + '\n')
    f.close()

    f = open(edges_store_filepath, 'a')
    f.write(str(cnt) + ' @@ ' + filepath_all + ' @@ ' + func_name + '\n')
    for edge in sorted_edges:
        f.write(str(edge[0]) + "," + str(edge[1]) + '\n')
    f.write('------------------------------' + '\n')
    f.close()


def process_node(codeList,j):
    listnode=list(codeList)
    list_for_line = []
    for node in codeList:
    #     node['code'] = node['code'].replace('\n', ' ')
    #     if node['type'] == 'Function':
    #         f = open(node['filepath'], 'r')
    #         content = f.readlines()
    #         f.close()
    #         raw = int(node['location'].split(':')[0])-1
    #         code = content[raw].replace('\\', '').strip()

    #         new_code = ""
    #         if code.find("#define") != -1:
    #             node['code'] = code.replace('\n', ' ')
    #             continue
    #         while (len(code) >= 1 and code[-1] != ')' and code[-1] != '{' and code[-5:] != 'const'):
    #             if code.find('{') != -1:
    #                 index = code.index('{')
    #                 new_code += code[:index].strip()
    #                 node['code'] = new_code.replace('\n', ' ')
    #                 break
    #             else:
    #                 new_code += code + '\n'
    #                 raw += 1
    #                 code = content[raw].replace('\\', '').strip()
    #         else:
    #             new_code += code
    #             new_code = new_code.strip()
    #             if new_code[-1] == '{':
    #                 new_code = new_code[:-1].strip()
    #                 node['code'] = new_code.replace('\n', ' ')
    #             else:
    #                 node['code'] = new_code.replace('\n', ' ')

    #     elif node['type'] == 'Condition':
    #         raw = int(node['location'].split(':')[0])-1
    #         if raw in list_for_line:
    #             node['code'] = ''
    #             continue
    #         else:
    #             f = open(node['filepath'], 'r')
    #             content = f.readlines()
    #             f.close()
    #             code = content[raw].replace('\\', '').strip()
    #             pattern = re.compile("(?:if|while|for|switch)")
    #             res = re.search(pattern, code)
    #             if res == None:
    #                 raw = raw - 1
    #                 code = content[raw].replace('\\', '').strip()
    #                 new_code = ""

    #                 while (code != '' and code[-1] != ')' and code[-1] != '{'):
    #                     if code.find('{') != -1:
    #                         index = code.index('{')
    #                         new_code += code[:index].strip()
    #                         node['code'] = new_code.replace('\n', ' ')
    #                         list_for_line.append(raw)
    #                         break
    #                     else:
    #                         new_code += code + '\n'
    #                         list_for_line.append(raw)
    #                         raw += 1
    #                         code = content[raw].replace('\\', '').strip()
    #                 else:
    #                     new_code += code
    #                     new_code = new_code.strip()
    #                     if new_code[-1] == '{':
    #                         new_code = new_code[:-1].strip()
    #                         node['code'] = new_code.replace('\n', ' ')
    #                         list_for_line.append(raw)
    #                     else:
    #                         list_for_line.append(raw)
    #                         node['code'] = new_code.replace('\n', ' ')
    #             else:
    #                 res = res.group()
    #                 if res == '':
    #                     print ("error!")
    #                     exit()

    #                 elif res != 'for':
    #                     if (res + ' ( ') not in node['code']:
    #                         new_code = res + ' ( ' + node['code'] + ' ) '
    #                         node['code'] = new_code.replace('\n', ' ')
    #                 else:
    #                     new_code = ""
    #                     if code.find(' for ') != -1:
    #                         code = 'for ' + code.split(' for ')[1]

    #                     while code != '' and code[-1] != ')' and code[-1] != '{':
    #                         if code.find('{') != -1:
    #                             index = code.index('{')
    #                             new_code += code[:index].strip()
    #                             node['code'] = new_code.replace('\n', ' ')
    #                             list_for_line.append(raw)
    #                             break

    #                         elif code[-1] == ';' and code[:-1].count(';') >= 2:
    #                             new_code += code
    #                             node['code'] = new_code.replace('\n', ' ')
    #                             list_for_line.append(raw)
    #                             break

    #                         else:
    #                             new_code += code + '\n'
    #                             list_for_line.append(raw)
    #                             raw += 1
    #                             code = content[raw].replace('\\', '').strip()

    #                     else:
    #                         new_code += code
    #                         new_code = new_code.strip()
    #                         if new_code[-1] == '{':
    #                             new_code = new_code[:-1].strip()
    #                             node['code'] = new_code.replace('\n', ' ')
    #                             list_for_line.append(raw)

    #                         else:
    #                             list_for_line.append(raw)
    #                             node['code'] = new_code.replace('\n', ' ')

    #     elif node['type'] == 'Label':
    #         f = open(node['filepath'], 'r')
    #         content = f.readlines()
    #         f.close()
    #         raw = int(node['location'].split(':')[0])-1
    #         code = content[raw].replace('\\', '').strip()
    #         node['code'] = code.replace('\n', ' ')

    #     elif node['type'] == 'ForInit':
    #         node['code'] = ''

    #     elif node['type'] == 'Parameter':
    #         if codeList[0]['type'] != 'Function':
    #             node['code'] = node['code'].replace('\n', ' ')
    #         else:
    #             node['code'] = ''

    #     elif node['type'] == 'IdentifierDeclStatement':
    #         if node['code'].strip().split(' ')[0] == "undef":
    #             f = open(node['filepath'], 'r')
    #             content = f.readlines()
    #             f.close()
    #             raw = int(node['location'].split(':')[0])-1
    #             code1 = content[raw].replace('\\', '').strip()
    #             list_code2 = node['code'].strip().split(' ')
    #             i = 0
    #             while i < len(list_code2):
    #                 if code1.find(list_code2[i]) != -1:
    #                     del list_code2[i]
    #                 else:
    #                     break
    #             code2 = ' '.join(list_code2)
    #             node['code'] = code1.replace('\n', ' ') + ' ' + code2.replace('\n', ' ')
    #         else:
    #             node['code'] = node['code'].replace('\n', ' ')

    #     elif node['type'] == 'ExpressionStatement':
    #         if node['code']=='':
    #             continue
    #         row = int(node['location'].split(':')[0])-1
    #         if row in list_for_line:
    #             node['code'] = ''
    #         elif node['code'].strip()[-1] != ';':
    #             node['code'] = node['code'].replace('\n', ' ') + ' ;'
    #         else:
    #             node['code'] = node['code'].replace('\n', ' ')

    #     elif node['type'] == "Statement":
    #         node['code'] = node['code'].replace('\n', ' ')

    #     else:
    #         if node['location'] == None:
    #             node['code'] = ''
    #         else:
    #             row = int(node['location'].split(':')[0])-1
    #             if row in list_for_line:
    #                 node['code'] = ''
    #             else:
    #                 node['code'] = node['code'].replace('\n', ' ')

    # # delete null node
    # i = 0
    # while i < len(codeList):
    #     if codeList[i]['code'] in ['\n', '\t', ' ', '']:
    #         del codeList[i]
    #         # print(listnode[i]['code'])
    #     else:
    #         i += 1
        if node['type'] == "Condition":
            newcode=get_ast_parent_code(node['name'],j)
            node['code']=newcode

        elif node['type'] == "Function":
            newcode=get_func_def_code(node['name'],j)
            node['code']=newcode
        node['code'] = node['code'].replace('\n', ' ')
        
    return codeList


def getallpdgbytestID(testID):
    id2pdg={}
    path = os.path.join('pdg_db', testID)
    for _file in os.listdir(path):
        func_id=_file.split('_')[-1]
        fpath = os.path.join(path, _file)
        fin = open(fpath, 'rb')
        pdg = pickle.load(fin)
        fin.close()
        id2pdg[func_id]=pdg
    return id2pdg

def program_slice(pdg, Startnode, testID, slicetype,j):

    startnodesID=Startnode[0]
    startnode=None
    for node in pdg.vs:
        if node['name'] ==startnodesID:
            startnode=node

    if startnode == None:
        return [], []

    ret_starnodes=[]
    ret_graphs=[]

    if slicetype == 0:  # backwards

        subgraph_bak  = program_slice_backwards(pdg,startnode)
        iter_times_cross=1
        current_time_cross=0

        sub_graph_cross= process_cross_func(iter_times_cross,current_time_cross, testID, subgraph_bak,j)
        ret_graphs.append(sub_graph_cross)
        ret_starnodes.append(startnode)
        return ret_graphs,ret_starnodes


    elif slicetype == 1:  # forwards

        subgraph_for= program_slice_forward(pdg, [startnode])

        iter_times_cross = 1
        current_time_cross=0

        # 向下跨函数切片，iter_times跨函数层数
        subgraph_cross= process_cross_func(iter_times_cross,current_time_cross, testID, subgraph_for,j)

        #向下需要return back 2022.9.22 wanghu
        funcid=startnode['functionId']
        allnodes=sortedNodesByLoc(subgraph_for.vs())
        iter_times_retback=1
        current_time_retback=0
        subgraphlist = process_return_back(iter_times_retback,current_time_retback,allnodes[-1],funcid,subgraph_cross,testID,5,j)

        for graph in subgraphlist:
            ret_graphs.append(graph)
            ret_starnodes.append(startnode)


        return ret_graphs, ret_starnodes


def pointer_slice(j):
    slice_store_filepath = "./slice_source/pointer_slices.txt"  # 存储切片的结果
    edges_store_filepath = "./edges_source/pointer_edges.txt"  # 存储edges
    f=open(slice_store_filepath,'w+')
    f.close()
    f=open(edges_store_filepath,'w+')
    f.close()
    f = open("pointdef_slice_points.pkl", 'rb')
    edit_points = pickle.load(f)
    f.close()
    i=0
    len1=len(edit_points)
    cnt = 0
    hashList = []
    slice_type = 1#指针往下切

    for fileID in edit_points.keys():
        print('\r',end='')
        print('slice pointer:',i,'/',len1,end=' ')
        # if i<3:
        #     i+=1
        #     continue
        i+=1

        testID = fileID.split('/')[-2]
        for func_info in edit_points[fileID]:
            # print(cnt,'/',len(edit_points[fileID]))
            # if cnt<2:
            #     cnt+=1
            #     continue
            funcID = func_info.split('-')[0]
            func_name = func_info.split('-')[1]
            pdg = getFuncPDGById(testID, funcID)  # get pdg from pdg_db
            if pdg == False or pdg == None:
                continue

            start_nodes = edit_points[fileID][func_info]
            var_list = []
            for node in start_nodes:
                for var in node[3]:
                    if var not in var_list:
                        var_list.append(var)

            all_results, all_edges, ret_startnodes = program_slice(pdg, start_nodes, testID, slice_type)

            if all_results == []:
                fout = open("error.txt", 'a')
                fout.write(str(start_nodes) + ' found nothing! \n')
                fout.close()
            else:
                for list_code, list_edge,start_node in zip(all_results, all_edges,ret_startnodes):
                    contents = ""
                    for node in list_code:
                        contents += node['code']
                    hashNum = hash(contents)    # hash去重
                    if hashNum not in hashList:
                        cnt += 1
                        hashList.append(hashNum)
                        # check_node_edge(list_code,list_edge)

                        process_node(list_code,j)  # 完善节点的code属性
                        # check_node_edge(list_code,list_edge)

                        startpath = start_node['filepath']
                        startline1=start_node['location'].split(':')[0]
                        startcode= start_node['code']

                        get_slice_file_sequence(slice_store_filepath, edges_store_filepath, list_code, list_edge, cnt,
                                                func_name, startline1, startpath, startcode)  # var_list关键变量列表


def array_slice(j):
    slice_store_filepath = "./slice_source/array_slices.txt"  # 存储切片的结果
    edges_store_filepath = "./edges_source/array_edges.txt"  # 存储edges
    f=open(slice_store_filepath,'w+')
    f.close()
    f=open(edges_store_filepath,'w+')
    f.close()
    f = open("arraydef_slice_points.pkl", 'rb')
    edit_points = pickle.load(f)
    f.close()
    cnt = 0
    hashList = []
    i=0
    slice_type = 1#数组往下切片

    len1=len(edit_points)
    for fileID in edit_points.keys():
        print('\r',end='')
        print('slice array:',i,'/',len1,end=' ')
        i+=1

        testID = fileID.split('/')[-2]
        for func_info in edit_points[fileID]:
            funcID = func_info.split('-')[0]
            func_name = func_info.split('-')[1]
            pdg = getFuncPDGById(testID, funcID)  # get pdg from pdg_db
            if pdg == False or pdg == None:
                continue

            start_nodes = edit_points[fileID][func_info]
            var_list = []
            for node in start_nodes:
                for var in node[3]:
                    if var not in var_list:
                        var_list.append(var)

            all_results, all_edges, ret_startnodes = program_slice(pdg, start_nodes, testID, slice_type)

            if all_results == []:
                fout = open("error.txt", 'a')
                fout.write(str(start_nodes) + ' found nothing! \n')
                fout.close()
            else:
                for list_code, list_edge,start_node in zip(all_results, all_edges,ret_startnodes):
                    contents = ""
                    for node in list_code:
                        contents += node['code']
                    hashNum = hash(contents)    # hash去重
                    if hashNum not in hashList:
                        cnt += 1
                        hashList.append(hashNum)
                        # check_node_edge(list_code,list_edge)

                        process_node(list_code,j)  # 完善节点的code属性
                        # check_node_edge(list_code,list_edge)

                        startpath = start_node['filepath']
                        startline1=start_node['location'].split(':')[0]
                        startcode= start_node['code']

                        get_slice_file_sequence(slice_store_filepath, edges_store_filepath, list_code, list_edge, cnt,
                                                func_name, startline1, startpath, startcode)  # var_list关键变量列表

def check_node_edge(nodes,edges):
    node_ids=set()
    for node in nodes:
        node_ids.add(node['name'])
    edge_node_ids=set()
    for edge in edges:
        edge_node_ids.add(edge[0])
        edge_node_ids.add(edge[1])
    i=0
    for id in edge_node_ids:
        if id not in node_ids:
            i+=1
    print(i,len(edge_node_ids))

def api_slice(j):
    slice_store_filepath = "./slice_source/api_slices.txt"  # 存储切片的结果
    edges_store_filepath = "./edges_source/api_edges.txt"  # 存储edges
    f=open(slice_store_filepath,'w+')#清空原来的文件
    f.close()
    f=open(edges_store_filepath,'w+')#清空原来的文件
    f.close()
    f = open("sensifunc_slice_points.pkl", 'rb')
    edit_points = pickle.load(f)
    f.close()
    i=0
    len1=len(edit_points)
    hashList = []
    cnt = 0
    slice_type = 0#api切片仅往上切
    for fileID in edit_points.keys():
        print('\r',end='')
        print('slice api:',i,'/',len1,' ',end='')
        i+=1
        
        testID = fileID.split('/')[-2]

        for func_info in edit_points[fileID]:
            funcID = func_info.split('-')[0]
            func_name = func_info.split('-')[1]
            pdg = getFuncPDGById(testID, funcID)  # get pdg from pdg_db
            if pdg == False or pdg == None:
                continue

            start_nodes = edit_points[fileID][func_info]
            var_list = []
            for node in start_nodes:
                for var in node[3]:
                # var=node[2]
                    if var not in var_list:
                        var_list.append(var)

            # slice_type为1表示向下切片，slice_type为0表示向上切片
            all_results, all_edges, ret_startnodes  = program_slice(pdg, start_nodes, testID, slice_type)
            # print(len(ret),ret)
            if all_results == []:
                fout = open("error.txt", 'a')
                fout.write(str(start_nodes) + ' found nothing! \n')
                fout.close()
            else:
                for list_code, list_edge,start_node in zip(all_results, all_edges,ret_startnodes):
                    contents = ""
                    for node in list_code:
                        contents += node['code']
                    hashNum = hash(contents)    # hash去重
                    if hashNum not in hashList:
                        cnt += 1
                        hashList.append(hashNum)
                        # check_node_edge(list_code,list_edge)

                        process_node(list_code,j)  # 完善节点的code属性
                        # check_node_edge(list_code,list_edge)

                        startpath = start_node['filepath']
                        startline1=start_node['location'].split(':')[0]
                        startcode= start_node['code']

                        get_slice_file_sequence(slice_store_filepath, edges_store_filepath, list_code, list_edge, cnt,
                                                func_name, startline1, startpath, startcode)  # var_list关键变量列表

def interger_overflow_slice(j):
    slice_store_filepath = "./slice_source/integer_overflow_slices.txt"  # 存储切片的结果
    edges_store_filepath = "./edges_source/integer_overflow_edges.txt"  # 存储edges
    f=open(slice_store_filepath,'w+')
    f.close()
    f=open(edges_store_filepath,'w+')
    f.close()
    f = open("integer_overflow_points.pkl", 'rb')
    edit_points = pickle.load(f)
    f.close()
    cnt = 0
    hashList = []
    i=0
    len1=len(edit_points)
    for fileID in edit_points.keys():
        print('\r',end='')
        print('slice expr:',i,'/',len1,end=' ')
        i+=1

        # slice_type = 0#api切片仅往上切
        testID = fileID.split('/')[-2]
        for func_info in edit_points[fileID]:
            funcID = func_info.split('-')[0]
            func_name = func_info.split('-')[1]
            pdg = getFuncPDGById(testID, funcID)  # get pdg from pdg_db
            if pdg == False or pdg == None:
                continue

            start_nodes = edit_points[fileID][func_info]
            var_list = []
            for node in start_nodes:
                # for var in node[3]:
                var=node[2]
                if var not in var_list:
                    var_list.append(var)
            all_results=[]
            all_edges=[]
            ret_startnodes=[]
            # slice_type为1表示向下切片，slice_type为0表示向上切片
            all_results1, all_edges1, ret_startnodes1 = program_slice(pdg, start_nodes, testID, 0)
            all_results2, all_edges2, ret_startnodes2 = program_slice(pdg, start_nodes, testID, 1)
            for nodes1,edges1 in zip(all_results1,all_edges1):
                for nodes2,edges2 in zip(all_results2,all_edges2):
                    if nodes1[-1]==nodes2[0]:
                        all_results.append(nodes1+nodes2[1:])
                        all_edges.append(edges1|edges2)
                        ret_startnodes.append(nodes1[-1])

            # all_results=all_results1+all_results2
            # all_edges=[all_edges1[0]|all_edges2[0]]
            if all_results == []:
                fout = open("error.txt", 'a')
                fout.write(str(start_nodes) + ' found nothing! \n')
                fout.close()
            else:
                for list_code, list_edge,start_node in zip(all_results, all_edges,ret_startnodes):
                    contents = ""
                    for node in list_code:
                        contents += node['code']
                    hashNum = hash(contents)    # hash去重
                    if hashNum not in hashList:
                        cnt += 1
                        hashList.append(hashNum)
                        # check_node_edge(list_code,list_edge)

                        process_node(list_code,j)  # 完善节点的code属性
                        # check_node_edge(list_code,list_edge)

                        startpath = start_node['filepath']
                        startline1=start_node['location'].split(':')[0]
                        startcode= start_node['code']

                        get_slice_file_sequence(slice_store_filepath, edges_store_filepath, list_code, list_edge, cnt,
                                                func_name, startline1, startpath, startcode)  # var_list关键变量列表
def type_slice(type,j,cnt):
    slice_store_filepath = "./slice_source/%s_slices.txt"%type  # 存储切片的结果
    edges_store_filepath = "./edges_source/%s_edges.txt"%type  # 存储edges
    f=open(slice_store_filepath,'w+')
    f.close()
    f=open(edges_store_filepath,'w+')
    f.close()
    f = open("%s_points.pkl"%type, 'rb')
    edit_points = pickle.load(f)
    f.close()
    # cnt = 0
    hashList = []
    i=0
    len1=len(edit_points)
    for fileID in edit_points.keys():
        
        # slice_type = 0#api切片仅往上切
        testID = fileID.split('/')[-2]
        for func_info in edit_points[fileID]:
            print('\r',end='')
            print('slice %s:'%type,i,'/',len1,end=' ')
            i+=1

            funcID = func_info.split('-')[0]
            func_name = func_info.split('-')[1]
            pdg = getFuncPDGById(testID, funcID)  # get pdg from pdg_db
            if pdg == False or pdg == None:
                continue

            start_nodes = edit_points[fileID][func_info]

            allgraph=[]
            all_retstartnodes=[]

            for startnode in start_nodes:
            # slice_type为1表示向下切片，slice_type为0表示向上切片

                graphs1=[]
                graphs2=[]
                ret_startnodes1=[]
                ret_startnodes2=[]
                if type in ['api','integer_overflow']:
                    graphs1,ret_startnodes1 = program_slice(pdg, startnode, testID, 0,j)
                if type in ['pointer','array','integer_overflow']:
                     graphs2,ret_startnodes2 = program_slice(pdg, startnode, testID, 1,j)

                if graphs1==[]:
                    allgraph+=graphs2
                    all_retstartnodes+=ret_startnodes2
                elif graphs2==[]:
                    allgraph+=graphs1
                    all_retstartnodes+=ret_startnodes1
                else:
                    for k in range(len(graphs1)):
                        for l in range(len(graphs2)):
                            newgraph=graphs1[k].union(graphs2[l])
                            allgraph.append(newgraph)
                            all_retstartnodes.append(ret_startnodes1[k])


            if allgraph == []:
                fout = open("error.txt", 'a')
                fout.write(str(start_nodes) + ' found nothing! \n')
                fout.close()
            else:
                for graph,start_node in zip(allgraph, all_retstartnodes):
                    
                    list_edge=[]
                    contents = ""
                    for node in graph.vs():
                        contents += node['code']
                    hashNum = hash(contents)    # hash去重
                    if hashNum not in hashList:
                        cnt += 1
                        hashList.append(hashNum)
                        # check_node_edge(list_code,list_edge)

                        process_node(graph.vs(),j)  # 完善节点的code属性
                        # check_node_edge(list_code,list_edge)

                        startpath = start_node['filepath']
                        startline1=start_node['location'].split(':')[0]
                        startcode= start_node['code']
                        for edge in graph.es():
                            list_edge.append((edge.source_vertex['name'],edge.target_vertex['name']))
                        get_slice_file_sequence(slice_store_filepath, edges_store_filepath, graph.vs(), list_edge, cnt,
                                                func_name, startline1, startpath, startcode)  # var_list关键变量列表
                        if not os.path.exists('./slice_graph'):
                            os.mkdir('./slice_graph')
                        
                        f=open(os.path.join('./slice_graph',fileID.split('/')[-1]+'@@'+func_name+'@@'+str(cnt)+'.pkl'),'wb')
                        pickle.dump(graph,f)
                        f.close()
    return cnt

if __name__ == "__main__":
    if(not os.path.exists('./slice_source')):
        os.makedirs('./slice_source')
    if(not os.path.exists('./edges_source')):
        os.makedirs('./edges_source')

    j = JoernSteps()
    j.connectToDatabase()
    cnt=0
    for type in ['api','array','pointer','integer_overflow']:
                                  cnt=type_slice(type,j,cnt)


#1.向上切片，跨函数是从return开始向上切。
#2.向下切片，从参数往下切片，若无参数，则将整个pdg加入。
#3.向下切片，是否需要删除控制流。
#4.return back是否需要迭代，是否需要cross func