# coding:utf-8
from __future__ import print_function
from access_db_operate import *
import  sys

def rmv_str(s):  # 去除了字符串
    while "\'" in s:
        indL = s.find('\'')
        if '\'' in s[indL + 1:]:
            indR = s.find('\'', indL+1)
            s = s[:indL] + s[indR+1:]
        else:
            s = s[:indL] + s[indL + 1:]

    while "\"" in s:
        indL = s.find('\"')
        if '\"' in s[indL + 1:]:
            indR = s.find('\"', indL+1)
            s = s[:indL] + s[indR+1:]
        else:
            s = s[:indL] + s[indL + 1:]
    return s

# 用比较符截断比较式的语句


def get_location(s):
    if(s.find(' < ') != -1):
        # print("1")
        return s.find(' < ')

    elif(s.find(' > ') != -1 and s.find(' -> ') == -1):
        # print("2")
        return s.find(' > ')

    elif(s.find(' <= ') != -1):
        # print("3")
        return s.find(' <= ')

    elif(s.find(' >= ') != -1):
        # print("4")
        return s.find(' >= ')

    elif(s.find(' == ') != -1):
        # print("5")
        return s.find(' == ')

    elif(s.find(' != ') != -1):
        # print("6")
        return s.find(' != ')
    else:
        return -2

# 判断是不是数字


def is_number(s):
    if(s[:2] == '0x'):
        return True
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def is_define(s):  # isupper
    ss = s.replace('_', '')
    if(ss.isupper()):
        return True
    else:
        return False


def check_var_again(res_vars):
    var_list = []
    var_tmp = []
    for res in res_vars:
        if '::' in res:
            loc = res.rfind("::")
            res = res[loc+1:]
        res = res.strip()
        while res != '' and len(res) != 1 and (res[0] == '(' or res[0] == ')' or res[0] == '-' or res[0] == '+' or res[0] == '~' or res[0] == '|' or res[0] == '<' or res[0] == '>' or res[0] == '/' or res[0] == '|' or res[0] == '!' or res[0] == '{' or res[0] == '}' or res[0] == '=' or res[0] == ':' or res[0] == ','):
            res = res[1:].strip()
            if res == '':
                continue
        while res != '' and len(res) != 1 and (res[-1] == '(' or res[-1] == ')' or res[-1] == '|' or res[-1] == '-' or res[-1] == '+' or res[-1] == '<' or res[-1] == '>' or res[-1] == '/' or res[-1] == '%' or res[-1] == '*' or res[-1] == '&' or res[-1] == '{' or res[-1] == '}' or res[-1] == ';' or res[-1] == '=' or res[-1] == ':' or res[-1] == ','):
            res = res[:-1].strip()
            if res == '':
                continue

        if res == '':
            continue

        if res == 'int' or res == 'char' or 'size_t' in res or 'signed' in res or 'float' in res or res == 'struct' or res.startswith('uint') or res == 'void' or res == 'const':
            continue

        pat = re.compile(r'.*\[(.*?)\].*', re.MULTILINE)  # 看是不是数组变量
        flag = pat.findall(res)  # 检查=前面，也就是变量所在的位置有没有[]
        locL = res.find("[")
        locR = res.find("]")

        if (flag):  # 去除数组末尾的符号
            ind = res[:locL].find("-")
            if ind == -1:
                ind = res[locR+1:].find("-")
        else:
            ind = res.find('-')

        if ind != -1:
            if ind>=len(res)-1:
                continue
            if is_number(res[ind+1]):  # 变量提取出来是否有a-1这种表达式
                res = res[:ind]
                var_tmp.append(res)
            elif res[ind+1] != '>' and res[ind+1:ind+3] != ' >' and res[ind+1] != '-':  # a - b的形式
                var_tmp.append(res[:ind])
                var_tmp.append(res[ind+1:])
            else:
                var_tmp.append(res)
        else:
            var_tmp.append(res)

    for res in var_tmp:
        flag_al = 0
        for r in res:
            if r.isalpha():
                flag_al = 1
                break
        if flag_al == 1:
            if (is_number(res) != True) and (is_define(res) != True):
                if res.count("[") != res.count("]"):
                    if res.find("[") != -1:
                        res = res.split("[")[0]
                    else:
                        res = res.split(']')[-1]
                if res.count("(") == res.count(")"):
                    var_list.append(res.strip())

    res_vars = [i for i in var_list if ((i != '') and (i != "\'") and (i != '\"') and (i != '-') and (i != '+') and (i != '/') and (i != '<') and (i != '>') and (
        i != '!') and (i != '=') and (i != '*') and (i != '&') and (i != '<=') and (i != '>=') and (i != '==') and (i != '<<') and (i != '>>'))]  # 去除空和其它字符
    res_vars = list(set(res_vars))
    return res_vars

# 获取API调用的关键变量
# flag=1表示函数调用，flag=2表示函数头部main


def get_call_var(s, flag):
    # if 'spprintf' in s or 'E_WARNING' in s or 'warning' in s or 'assert' in s or 'print' in s or 'ASSERT' in s or 'Exception' in s or 'Error' in s or 'FAIL' in s:
    #     return []
    # print (s)
    s = rmv_str(s)
    if s[1:].strip().startswith('(') and not s[1:].strip().startswith('(('):  # 去除 (void) func(a,b);情况中的(void)
        indR = s[1:].strip().find(")")
        s = s[1:].strip()[indR+1:]

    start = s.find('(')
    end = s.rfind(')')

    if((start != -1) and (end != -1)):
        res = s[start + 1:end]  # 已经去掉了括号
    elif(start != -1):
        res = s[start + 1:]
    elif(end != -1):
        res = s[:end]
    else:
        print("error")
        return []

    res = re.split('[,]', res)  # 以逗号分割实参，将实参单独提出
    res = [i for i in res if i != '']  # 去除空
    res_vars = []

    for i in res:
        if i.strip() == '':
            continue
        if(i[0] == ' '):
            i = i[1:]
        if(i[0] == '\"' and i[-1] == '\"'):  # 如果是字符换就不输出了
            continue
        if(i[0] == '\'' and i[-1] == '\''):  # 如果是字符换就不输出了
            continue
        if flag == 2:
            res_vars.append(i.split(' ')[-1])  # 去除变量类型
        else:     # 分割函数参数中存在的表达式 提取出变量
            sym_L = i.rfind('<')
            sym_R = i.find(">")
            if sym_R != -1 and sym_L != -1 and '->' not in i[sym_L:sym_R] and ' ' not in i[sym_L:sym_R]:
                i = i.split(">")[-1]
            i_list = re.split('&&|[||]', i)
            i_list = [k for k in i_list if k != '']  # 去除空
            for j in i_list:
                j = j.strip()

                if "(" in j and ')' not in j:  # 函数调用里面还有函数调用，套娃专用
                    ind = j.find('(')
                    j = j[ind+1:].strip()

                if '(' in j and ')' in j:  # (const int) a
                    locL = j.rfind('(')
                    locR = j.find(')')
                    if locL < locR:
                        if locR != len(j) - 1:  # (const int) a / sizeof(registered_avfilters)
                            j = j.split(')')[-1]
                        else:
                            if locR != locL + 1:
                                j = j[locL+1: locR]
                    else:
                        j = j[locL+1:]

                index = get_location(j)
                if(index != -2):
                    j = j[:index]

                j = j.strip()
                j_list = re.split('[, ]|[ + ]|[ - ]|[ * ]|[ / ]|[; ][ & ]|[+]|[*]|[/]', j)
                j_list = [m for m in j_list if ((m != '') and (m != '-') and (m != '+') and (m != '/') and (m != '*') and (m != '&'))]  # 去除空和其它字符
                for k in j_list:  # 处理每一个实参表达式, 去除表达式中的括号
                    if((is_number(k) == False) and (is_define(k) == False)):
                        if '(' in k and ')' not in k:
                            inde = k.find("(")
                            k = k[inde+1:]
                            res_vars.append(k)
                        else:
                            res_vars.append(k)

    res_vars2 = check_var_again(res_vars)
    return res_vars2


def get_all_sensitiveAPI(db,funcids):
    fin = open("sensitive_func.pkl", 'rb')
    list_sensitive_funcname = pickle.load(fin)
    fin.close()

    _dict = {}
    for func_name in list_sensitive_funcname:
        if func_name.find('main') != -1:
            continue
        else:
            list_callee_id = get_calls_id(db, func_name)  # 所有函数调用节点
            if list_callee_id == []:
                continue
            for _id in list_callee_id:
                cfgnode = getCFGNodeByCallee(db, _id)  # 向上寻找第一个cfg顶点
                if cfgnode != None:
                    funcID = cfgnode.properties['functionId']
                    if funcID not in funcids:
                        continue
                    name = cfgnode.properties['code'].strip()
                    nodeType = cfgnode.properties['type'].strip()
                    nodeloc = int(cfgnode['location'].split(':')[0])
                    list_vars = get_call_var(name, 1)  # 应该是函数参数

                    funcName = getNameByNodeid(db, funcID)
                    funcInfo = str(funcID)+"-"+funcName
                    filepath = getFuncFile(db, int(cfgnode.properties['functionId']))
                    if filepath in _dict.keys():
                        if funcInfo in _dict[filepath].keys():
                            _dict[filepath][funcInfo].append((str(cfgnode._id), str(nodeType), name, list_vars, nodeloc))
                        else:
                            _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, list_vars, nodeloc)]
                    else:
                        _dict[filepath] = {}
                        _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, list_vars, nodeloc)]

    return _dict
# _dict[filepath][funcInfo]二维字典


def get_all_pointer(db,funcids):
    _dict = {}
    list_pointers_node = get_pointers_node(db)  # 只能获得声明语句 ---可以获得声明语句和参数2022.09.23 wanghu
    for cfgnode in list_pointers_node:
        funcID = cfgnode.properties['functionId']
        if funcID not in funcids:
            continue
        if cfgnode['location']==None:
            continue
        pointer_name = []
        pointer_defnode = get_def_node(db, cfgnode._id)  # 为了获得变量名
        for node in pointer_defnode:
            name = node.properties['code'].replace('*', '').strip()
            if name not in pointer_name:
                pointer_name.append(name)

        name = cfgnode.properties['code'].strip()
        nodeType = cfgnode.properties['type'].strip()
        nodeloc = int(cfgnode['location'].split(':')[0])

        funcName = getNameByNodeid(db, funcID)
        funcInfo = str(funcID)+"-"+funcName
        filepath = getFuncFile(db, int(cfgnode.properties['functionId']))
        if filepath in _dict.keys():
            if funcInfo in _dict[filepath].keys():
                _dict[filepath][funcInfo].append((str(cfgnode._id), str(nodeType), name, pointer_name, nodeloc))
            else:
                _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, pointer_name, nodeloc)]
        else:
            _dict[filepath] = {}
            _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, pointer_name, nodeloc)]

    return _dict


def get_all_array(db,funcids):
    _dict = {}
    list_arrays_node = get_arrays_node(db)
    for cfgnode in list_arrays_node:
        funcID = cfgnode.properties['functionId']

        if funcID not in funcids:
            continue
        array_name = []
        array_defnode = get_def_node(db, cfgnode._id)
        for node in array_defnode:
            name = node.properties['code'].replace('[', '').replace(']', '').replace('*', '').strip()
            if name not in array_name:
                array_name.append(name)

        name = cfgnode.properties['code'].strip()
        nodeType = cfgnode.properties['type'].strip()
        nodeloc = int(cfgnode['location'].split(':')[0])

        funcName = getNameByNodeid(db, funcID)
        funcInfo = str(funcID)+"-"+funcName
        filepath = getFuncFile(db, int(cfgnode.properties['functionId']))
        if filepath in _dict.keys():
            if funcInfo in _dict[filepath].keys():
                _dict[filepath][funcInfo].append((str(cfgnode._id), str(nodeType), name, array_name, nodeloc))
            else:
                _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, array_name, nodeloc)]
        else:
            _dict[filepath] = {}
            _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, array_name, nodeloc)]

    return _dict


def get_all_pointer_assignment(db):
    _dict = {}
    list_pointers_node = get_pointers_node(db)
    for cfgnode in list_pointers_node:
        _temp_list = []
        pointer_name = []
        pointer_defnode = get_def_node(db, cfgnode._id)
        for node in pointer_defnode:
            name = node.properties['code'].replace('*', '').strip()
            if name not in pointer_name:
                pointer_name.append(name)
        for node in pointer_defnode:
            name = node.properties['code'].strip()
            list_usenodes = get_all_use_bydefnode(db, node._id)
            list_defnodes = get_all_def_bydefnode(db, node._id)

            for node in list_defnodes:
                if node['location'] == None:
                    continue
                if node._id in _temp_list:
                    continue
                else:
                    _temp_list.append(node._id)

                name = node.properties['code'].strip()
                nodeType = node.properties['type'].strip()
                nodeloc = int(node['location'].split(':')[0])

                funcID = node.properties['functionId']
                funcName = getNameByNodeid(db, funcID)
                funcInfo = str(funcID)+"-"+funcName
                filepath = getFuncFile(db, int(node.properties['functionId']))
                if filepath in _dict.keys():
                    if funcInfo in _dict[filepath].keys():
                        _dict[filepath][funcInfo].append((str(node._id), str(nodeType), name, pointer_name, nodeloc))
                    else:
                        _dict[filepath][funcInfo] = [(str(node._id), str(nodeType), name, pointer_name, nodeloc)]
                else:
                    _dict[filepath] = {}
                    _dict[filepath][funcInfo] = [(str(node._id), str(nodeType), name, pointer_name, nodeloc)]
    return _dict


def get_all_array_assignment(db):
    _dict = {}
    list_arrays_node = get_arrays_node(db)  # 获取数组定义的地方，分为函数内部定义以及函数参数两部分
    for cfgnode in list_arrays_node:
        _temp_list = []
        array_name = []
        array_defnode = get_def_node(db, cfgnode._id)
        for node in array_defnode:
            name = node.properties['code'].replace('[', '').replace(']', '').replace('*', '').strip()
            if name not in array_name:
                array_name.append(name)
        for node in array_defnode:
            name = node.properties['code'].strip()
            # list_usenodes = get_all_use_bydefnode(db, node._id)
            list_defnodes = get_all_def_bydefnode(db, node._id)

            for node in list_defnodes:
                if node['location'] == None:
                    continue
                if node._id in _temp_list:
                    continue
                else:
                    _temp_list.append(node._id)

                name = node.properties['code'].strip()
                nodeType = node.properties['type'].strip()
                nodeloc = int(node['location'].split(':')[0])

                funcID = node.properties['functionId']
                funcName = getNameByNodeid(db, funcID)
                funcInfo = str(funcID)+"-"+funcName
                filepath = getFuncFile(db, int(node.properties['functionId']))
                if filepath in _dict.keys():
                    if funcInfo in _dict[filepath].keys():
                        _dict[filepath][funcInfo].append((str(node._id), str(nodeType), name, array_name, nodeloc))
                    else:
                        _dict[filepath][funcInfo] = [(str(node._id), str(nodeType), name, array_name, nodeloc)]
                else:
                    _dict[filepath] = {}
                    _dict[filepath][funcInfo] = [(str(node._id), str(nodeType), name, array_name, nodeloc)]
    return _dict


def get_all_integeroverflow_point(db,funcids):
    _dict = {}
    list_exprstmt_node = get_exprstmt_node(db)
    flag = 0
    for cfgnode in list_exprstmt_node:
        funcID = cfgnode.properties['functionId']
        if funcID not in funcids:
            continue
        if cfgnode['location']==None:
            continue
        flag = 0
        if cfgnode.properties['code'].find(' = ') > -1:
            code = cfgnode.properties['code'].split(' = ')[-1]
            pattern = re.compile("((?:_|[A-Za-z])\w*(?:\s(?:\+|\-|\*|\/)\s(?:_|[A-Za-z])\w*)+)")
            result = re.search(pattern, code)

            if result == None:
                continue
            else:
                flag = 1
                # file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
                # testID = file_path.split('/')[-2]
                # name = cfgnode.properties['code'].strip()

                # if testID in _dict.keys():
                #     _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
                # else:
                #     _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]

        else:
            code = cfgnode.properties['code']
            pattern = re.compile("(?:\s\/\s(?:_|[A-Za-z])\w*\s)")
            result = re.search(pattern, code)
            if result == None:
                continue

            else:
                flag = 1
                # file_path = getFuncFile(db, int(cfgnode.properties['functionId']))
                # testID = file_path.split('/')[-2]
                # name = cfgnode.properties['code'].strip()

                # if testID in _dict.keys():
                #     _dict[testID].append(([str(cfgnode._id)], str(cfgnode.properties['functionId']), name))
                # else:
                #     _dict[testID] = [([str(cfgnode._id)], str(cfgnode.properties['functionId']), name)]
        if flag:
            name = cfgnode.properties['code'].strip()
            nodeType = cfgnode.properties['type'].strip()
            nodeloc = int(cfgnode['location'].split(':')[0])

            
            funcName = getNameByNodeid(db, funcID)
            funcInfo = str(funcID)+"-"+funcName
            filepath = getFuncFile(db, int(cfgnode.properties['functionId']))
            if filepath in _dict.keys():
                if funcInfo in _dict[filepath].keys():
                    _dict[filepath][funcInfo].append((str(cfgnode._id), str(nodeType), name,  nodeloc))
                else:
                    _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, nodeloc)]
            else:
                _dict[filepath] = {}
                _dict[filepath][funcInfo] = [(str(cfgnode._id), str(nodeType), name, nodeloc)]
    return _dict

def get_funcid_by_linenum_filename(db,linenum,filename):
    query_str = "queryNodeIndex('location:%s*').filter{it.location.contains('%s:')}.functions().dedup().id"%(linenum,linenum)
    # query_str = '''queryNodeIndex("location:147*").filter{it.location.contains('147:')}.functions().dedup().in('IS_FILE_OF').filepath.filter{it.contains('3ed264870942a7947792a108603bd866f465ce5c')}'''
    results = db.runGremlinQuery(query_str)
    if results==[]:
        return False
    # print(results)
    func_id=set()
    for funcid in results:
        query_str="g.v(%d).in('IS_FILE_OF').filepath"%funcid
        filepath = j.runGremlinQuery(query_str)[0]
        if filename in filepath:
            # print(filepath) 
            func_id.add(funcid)
    if len(func_id)==0:

        # print('get funcid wrong')
        return False

    return list(func_id)[0]
    

def get_funcid_by_filepath(db,filepath,filetype,old_or_new):
    if filetype=='funded':
        f=open('/home/lyl/useful/graph_slice/code/pkl/cwe2file2linenum_%s.pkl'%old_or_new,'rb')
        cwe2file2linenum=pickle.load(f)
        f.close()
        cwe=filepath.split('/')[-2]
        func_ids=set()
        for filename in os.listdir(filepath):
            if filename[:-2]in cwe2file2linenum[cwe]:
                linenums=cwe2file2linenum[cwe][filename[:-2]]
                for linenum in linenums:
                    func_id=get_funcid_by_linenum_filename(db,linenum,filename)
                    func_ids.add(func_id)
        return func_id
    elif filetype =='NVD':
        cwe=filepath.split('/')[-5]
        batch=filepath.split('/')[-3]
        cve=filepath.split('/')[-2]
        print(filepath)
        f=open('/home/lyl/huawei_project/code/pkl/%s_%s.pkl'%(cwe,old_or_new),'rb')
        file2linenum=pickle.load(f)
        f.close()
        func_ids=set()
        if old_or_new=='old':
            file2funcname={}
        else:
            f=open('/home/lyl/huawei_project/code/pkl/%s_file2funcname_%s.pkl'%(cve,batch),'rb')
            file2funcname=pickle.load(f)
            f.close()
            # print(file2funcname)
        for filename in os.listdir(filepath):
            funcids_file=set()
            if filename[:-8]in file2linenum:
                linenums=file2linenum[filename[:-8]]
                for linenum in linenums:
                    func_id=get_funcid_by_linenum_filename(db,linenum,filename)
                    i=0
                    while func_id==False:
                        i+=1
                        func_id=get_funcid_by_linenum_filename(db,linenum-i,filename)
                        if i>3:
                            break
                    if func_id==False:
                        print("can't find funcid")
                        continue
                    funcids_file.add(func_id)
            func_ids=func_ids|funcids_file
            if old_or_new=='old':
                funcnames=get_funcname_by_funcid(funcids_file)
                file2funcname[filename[:-8]]=funcnames
            else:
                funcnames=file2funcname[filename[:-8]]
                funcids=get_funcid_by_funcname(funcnames)
                func_ids=func_ids|funcids
        if old_or_new=='old':
            f=open('/home/lyl/huawei_project/code/pkl/%s_file2funcname_%s.pkl'%(cve,batch),'wb')      
            pickle.dump(file2funcname,f) 
            # print(file2funcname)
            f.close()

        return func_ids
def get_funcid_by_funcname(funcnames):
    funcids=set()
    for funcname in funcnames:
        query_str = "queryNodeIndex('type:Function AND name:%s').id"%funcname
        names = j.runGremlinQuery(query_str)
        for name in names:
            funcids.add(name)
    return funcids

def get_funcname_by_funcid(funcids):
    funcnames=set()
    for funcid in funcids:
        query_str="g.v(%d).name"%funcid
        funcname = j.runGremlinQuery(query_str)
        funcnames.add(funcname)
    return funcnames

if __name__ == '__main__':
    j = JoernSteps()
    j.connectToDatabase()
    filepath=sys.argv[1]
    filetype=sys.argv[2]
    new_or_old=sys.argv[3]
    # filepath='/home/lyl/huawei_project/NVD/CWE-119/merge/0/ffmpegCVE-2011-3929/new'
    # filetype='NVD'
    # new_or_old='new'

    funcids=get_funcid_by_filepath(j,filepath,filetype,new_or_old)
    # _dict = get_all_pointer_assignment(j)
    _dict = get_all_pointer(j,funcids)
    f = open("pointer_points.pkl", 'wb')
    pickle.dump(_dict, f, True)
    f.close()
    print ("pointer_def_points:",len(_dict)) #, _dict

    # _dict = get_all_array_assignment(j)
    _dict = get_all_array(j,funcids)
    f = open("array_points.pkl", 'wb')
    pickle.dump(_dict, f, True)
    f.close()
    print ("array_def_points:",len(_dict))#, _dict

    _dict = get_all_sensitiveAPI(j,funcids)
    f = open("api_points.pkl", 'wb')
    pickle.dump(_dict, f, True)
    f.close()
    print ("api_points:",len(_dict))#, _dict

    _dict = get_all_integeroverflow_point(j,funcids)
    f = open("integer_overflow_points.pkl", 'wb')
    pickle.dump(_dict, f, True)
    f.close()
    print ("integer_overflow_points:",len(_dict))#, _dict
