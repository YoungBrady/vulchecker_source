# -*- coding:utf-8 -*-
import pickle
import os
import random
import hashlib


# from attr import validate


def get_codes_labels_and_edges(path):

    slicedir = os.path.join(path, 'slice_source')
    # print(slicedir)
    edgesdir = os.path.join(path, 'edges_source')
    focus_list = ['api', 'array', 'integer_overflow', 'pointer']
    ret_list=[]
    for focus in focus_list:
        slice_file = os.path.join(slicedir, focus+'_slices.txt')
        edge_file = os.path.join(edgesdir, focus+'_edges.txt')

        # print(slice_file,edge_file)
        if not os.path.exists(slice_file):
            # print('slice not exists')
            continue
        if not os.path.exists(edge_file):
            # print('slice not exists')

            continue
        try:
            # slicelists=[]
            f = open(slice_file, "r",encoding='utf-8')
            slicelists = f.read().split('------------------------------\n')
            f.close()
        except Exception as e:
            print(e,slice_file,sep='\n')
        f = open(edge_file, "r",encoding='utf-8')
        edgelists = f.read().split('------------------------------\n')
        f.close()
        # print(slicelists)
        if slicelists == ['']:
            continue
        if edgelists == ['']:
            continue
        if slicelists[0] == '':
            del slicelists[0]
        if slicelists[-1] == '' or slicelists[-1] == '\n' or slicelists[-1] == '\r\n':
            del slicelists[-1]
        if edgelists[0] == '':
            del edgelists[0]
        if edgelists[-1] == '' or edgelists[-1] == '\n' or edgelists[-1] == '\r\n':
            del edgelists[-1]

        index = -1
        for slices in slicelists:
            index += 1
            # print('slice',len(slices))
            if slices == '':
                continue
            sentences = slices.split('\n')
            # print(sentence)
            if sentences[0] == '\r' or sentences[0] == '':
                del sentences[0]
            if sentences[-1] == '' or sentences[-1] == '\r':
                del sentences[-1]
            if sentences == []:
                continue

            # print('sentence0',sentences[0])
            if 'location:'in sentences[0] or 'file:'in sentences[0]:
                slice_all_len+=1
                continue
            filepath=sentences[0].split(' @@ ')[1].strip()
            # fileID = filepath.split('/')[-1][:-2]
            filename = filepath.split('/')[-1]
            fileid=('.').join(filename.split('.')[:-2])
            # cwe=filepath.split('/')[0]
            # if fileID not in old_dict[cwe] or fileID not in new_dict[cwe]:  # 如果标签不成对则跳过
            # if fileid not in old_dict or fileid not in new_dict:  # 如果标签不成对则跳过
            #     print('slice not match')
            #     continue
            funcID = sentences[0].split(' @@ ')[2]
            # sliceID = ('_').join(sentences[0].split(' @@ ')[:3])  # 切片标记
            starpath=filepath+'@@'+funcID
            code_list = []
            code_label_list = []
            # linenum_list=[]
            slice_name=sentences[0]+" "+focus
            sentences = sentences[1:]
            flag = False
            vulline_list=[]
            file_list=[]
            loc_list=[]
            for i in range(len(sentences)):
                sentence = sentences[i]
                this_file = sentence.split(' file: ')[-1].strip()      # 获取当前行的文件名
                this_code = sentence.split(' location: ')[0].replace('\n', ' ').strip()   # 获取当前行的代码片段
                this_loc = sentence.split(' location: ')[-1].split(' file: ')[0].strip()  # 获取当前行的行号
                code_list.append(this_code)
                loc_list.append(this_loc)
                file_list.append(this_file)


                code_label_list.append(random.randint(0,1))
   
            edges = edgelists[index].split('\n')
            if edges[0] == '\r' or edges[0] == '':
                del edges[0]
            if edges[-1] == '' or edges[-1] == '\r':
                del edges[-1]

 
            ret_list.append((code_list, code_label_list, edges,loc_list,file_list,starpath))

    # return code_label_edges
    # print(len(filepath2sample))
    return ret_list


def check_node_label(codes, edges):
    for edge in edges[1:]:
        a = int(edge.split(',')[0])
        b = int(edge.split(',')[1])
        if a<1 or b<1:
            return False
        if a > len(codes):
            return False
        if b > len(codes):
            return False
    return True
# def getSAGdata_batch(list_A,list_graph_indicator,list_graph_labels,list_node_labels,list_node_attributes_code,code_label_edges,type):
#     for tup in code_label_edges:
#         code_list,code_label_list,edges=tup
#         if check_node_label(code_list,edges)==False:
#             print(len(code_list),edges)
#             continue
#         for edge in edges[1:]:
#             a = int(edge.split(',')[0])
#             b = int(edge.split(',')[1])
#             new_a = a + len(list_node_attributes_code)
#             new_b = b + len(list_node_attributes_code)
#             list_A.append((new_a,new_b))
#         if type=='old':
#             list_graph_labels.append(1)
#         else:
#             list_graph_labels.append(0)

#         for code in code_list:
#             list_node_attributes_code.append(code)
#             list_graph_indicator.append(len(list_graph_labels))
#         list_node_labels+=code_label_list


# def getSAGdata_batch(list_A, list_graph_indicator, list_graph_labels, list_node_labels, list_node_attributes_code, code_label_edges, graph_num):
#     for tup in code_label_edges:
#         code_list, code_label_list, edges, type = tup
#         if check_node_label(code_list, edges) == False:
#             print(len(code_list), edges)
#             continue
#         for edge in edges[1:]:
#             a = int(edge.split(',')[0])
#             b = int(edge.split(',')[1])
#             new_a = a + len(list_node_attributes_code)
#             new_b = b + len(list_node_attributes_code)
#             list_A.append((new_a, new_b))
#         if type == 'old':
#             list_graph_labels.append(1)
#             graph_num[1] += 1
#         else:
#             list_graph_labels.append(0)
#             graph_num[0] += 1

#         for code in code_list:
#             list_node_attributes_code.append(code)
#             list_graph_indicator.append(len(list_graph_labels))
#         list_node_labels += code_label_list


def getSAGdata_batch(datatype,cle_tup_list):
    list_A = []
    list_graph_indicator = []
    list_graph_labels = []
    list_node_labels = []
    list_node_attributes_code = []
    SAGPool_Data_path = os.path.join('/home/sagpool/data/preprocess',datatype,'raw')
    # graph_num = [0, 0]

    slicename_list=[]

    all_loc=[]
    all_node_file=[]
    all_startpath=[]

    print('* '+datatype)
    print('graph num:', len(cle_tup_list))
    for i, tup in enumerate(cle_tup_list):
        code_list, code_label_list, edges, loc_list,file_list,starpath = tup

        all_loc+=loc_list
        all_node_file+=file_list
        all_startpath.append(starpath)
        ret=check_node_label(code_list, edges) 
        if not ret:
            print('* wrong',len(code_list), edges)
            continue
        for edge in edges[1:]:
            a = int(edge.split(',')[0])
            b = int(edge.split(',')[1])
            
            new_a = a + len(list_node_attributes_code)
            new_b = b + len(list_node_attributes_code)
           
            list_A.append((new_a, new_b))

        list_graph_labels.append(random.randint(0,1))


        for code in code_list:
            list_node_attributes_code.append(code)
            list_graph_indicator.append(len(list_graph_labels))
        list_node_labels += code_label_list

    # print(graph_num)

    if not os.path.exists(SAGPool_Data_path):
        os.makedirs(SAGPool_Data_path)


    # new_slice_name_list=[]
    # store_filepath = os.path.join(SAGPool_Data_path, "slicename_list.txt")
    # f = open(store_filepath, 'w+')
    # for i, slicename in enumerate(slicename_list) :
    #     tmp_list=slicename.split('@@')
    #     new_slice_name=tmp_list[1]+tmp_list[2]+tmp_list[4]
    #     new_slice_name_list.append(new_slice_name)
    #     f.write(slicename +str(vulline_list[i])+ '\n')
    # f.close()
    # store_filepath = os.path.join(SAGPool_Data_path, "slicename_list.pkl")
    # with open(store_filepath,'wb')as f:
    #     pickle.dump(new_slice_name_list,f)

    store_filepath = os.path.join(SAGPool_Data_path, f"{datatype}_A.txt")
    f = open(store_filepath, 'w+')
    for edge in list_A:
        f.write(str(edge[0]) + "," + str(edge[1]) + '\n')
    f.close()

    store_filepath = os.path.join(SAGPool_Data_path, f"{datatype}_graph_indicator.txt")
    f = open(store_filepath, 'w+')
    for dicator in list_graph_indicator:
        f.write(str(dicator) + '\n')
    f.close()

    store_filepath = os.path.join(SAGPool_Data_path, f"{datatype}_graph_labels.txt")
    f = open(store_filepath, 'w+')
    for label in list_graph_labels:
        f.write(str(label) + '\n')
    f.close()

    store_filepath = os.path.join(SAGPool_Data_path, f"{datatype}_attributes_code.txt")
    f = open(store_filepath, 'w+')
    for code in list_node_attributes_code:
        f.write(code + '\n')
    f.close()
    store_filepath = os.path.join(SAGPool_Data_path, f"{datatype}_node_labels.txt")
    f = open(store_filepath, 'w+')
    for label in list_node_labels:
        f.write(str(label) + '\n')
    f.close()

    # cve_list_store_path=os.path.join('/data/lh/wanghu/huawei_project/slice/SAGPool_Data',cwe,'cve_list.pkl')
    # f=open(cve_list_store_path,'wb')
    # pickle.dump(cve_list,f)
    # f.close()

    store_filepath = os.path.join(SAGPool_Data_path, "attributes_location.txt")
    f = open(store_filepath, 'w+')
    for loc in all_loc:
        f.write(loc + '\n')
    f.close()

    store_filepath = os.path.join(SAGPool_Data_path, "attributes_file.txt")
    f = open(store_filepath, 'w+')
    for file in all_node_file:
        f.write(file + '\n')
    f.close()

    store_filepath = os.path.join(SAGPool_Data_path, "graph_startpaths.txt")
    f = open(store_filepath, 'w+')
    for startpath in all_startpath:
        f.write(startpath + '\n')
    f.close()



def del_dup_slice(ret_list):
    hash2tup={}
 
    del_num=0
    for tup in ret_list:
        code_list, _, edges,_,_,_ = tup
        code_content=''
        for code in code_list:
            code_content+=code
        for edge in edges[1:]:
            code_content+=edge
        md5 = hashlib.md5()
        md5.update(code_content.encode('utf-8'))
        code_hash=md5.hexdigest()
        if code_hash in hash2tup:
            # print('dup')
            del_num+=1
            # hash2tup[code_hash]=None
        # else:
        hash2tup[code_hash]=tup#对于重复切片，用最新的替代
    
    
    
    ret_list=[]

    for hash_vale in hash2tup:
        ret_list.append(hash2tup[hash_vale])

    print('del num',del_num)
    # print('remian_num',len(ret_list))
    # if del_num!=[0,0]:
    #     print('oldnew_dup',del_num)
    return ret_list




if __name__ == '__main__':

    slice_root='/home/sagpool/data2slice/slice_all'
    ret_list=[]
    for batch in os.listdir(slice_root):
        ret=get_codes_labels_and_edges(os.path.join(slice_root,batch))
        ret_list+=ret

    del_dup_slice(ret_list)

    getSAGdata_batch('realdata', ret_list)
    # print(slice_all_len)


    