## coding:utf-8
from general_op import *
from Queue import Queue

def get_arguments(db,node_id):
    node_id = int(node_id)
    q = Queue(maxsize=100)
    q.put(node_id)
    nodes = []
    while not q.empty():
        node_id = q.get()
        query_with_var = "g.v(%d).children()" % node_id
        children = db.runGremlinQuery(query_with_var)
        for child in children:                        
            child_type = child['type']
            node_id = child._id
            node_code = child['code']
            if child_type == 'Argument':
                nodes.append(child)
            elif child_type == 'Identifier':
                continue
            else:
                q.put(node_id)
    return nodes

def get_child_type_for_AndOr(db, node_id):
    node_id = int(node_id)
    q = Queue(maxsize=100)
    q.put(node_id)
    # nodeId_type = {}
    node_list = []
    while not q.empty():
        node_id = q.get()
        query_with_var = "g.v(%d).children()" % node_id
        children = db.runGremlinQuery(query_with_var)
        for child in children:                        
            child_type = child['type']
            node_id = child._id
            node_code = child['code']
            if child_type == 'AndExpression' or child_type == 'OrExpression':
                q.put(node_id)
                continue
             
            else:
                node_list.append(child)
                
    return node_list

def get_cv_for_AndOr(db, node):
    node_type = node['type']
    node_code = node['code']
    node_id = int(node._id)
    varlist_in_condition = []

    if node_type == 'RelationalExpression' or node_type == 'EqualityExpression':# (a < 10)/ (a == 10)/ (a != 10)
        operator = node['operator']
        left_part_code  = node_code.split(operator)[0].replace(' ','')
        idents_name = get_all_identifiers_and_ptrArrMem_return_list(db, node_id)
        for ident in idents_name:
            if ident in left_part_code:
                varlist_in_condition.append(ident)

    elif node_type == 'UnaryOp' or node_type == 'IncDecOp': #(!a) / (a --)
        idents_name = get_all_identifiers_and_ptrArrMem_return_list(db, node_id)
        for ident in idents_name:
            varlist_in_condition.append(ident)

    elif node_type == 'CallExpression':
        argument_list = []
        argument_node_list = get_arguments(db, node_id)
        for argument in argument_node_list:
            argument_id = argument._id
            ident_list = get_all_identifiers_and_ptrArrMem_return_list(db, argument_id)
            for ident in ident_list:
                varlist_in_condition.append(ident)

    else:
        varlist_in_condition = condition_value_deliver(db, node_id)
    
    return varlist_in_condition

def condition_value_deliver(db, node_id):
    varlist_in_condition = []
    query_with_var = "g.v(%d).children()" % node_id
    children = db.runGremlinQuery(query_with_var)
    for child in children:
        child_type = child['type']
        child_code = child['code']
        child_id = child._id
        if child_type == 'RelationalExpression' or child_type == 'EqualityExpression':# (a < 10)/ (a == 10)/ (a != 10)
            operator = child['operator']
            left_part_code  = child_code.split(operator)[0].replace(' ','')
            idents_name = get_all_identifiers_and_ptrArrMem_return_list(db, child_id)
            for ident in idents_name:
                if ident in left_part_code:
                    varlist_in_condition.append(ident)

        elif child_type == 'UnaryOp' or child_type == 'IncDecOp': #(!a) / (a --)
            idents_name = get_all_identifiers_and_ptrArrMem_return_list(db, child_id)
            for ident in idents_name:
                varlist_in_condition.append(ident)

        elif child_type == 'CallExpression':
            argument_list = []
            argument_node_list = get_arguments(db, child_id)
            for argument in argument_node_list:
                argument_id = argument._id
                ident_list = get_all_identifiers_and_ptrArrMem_return_list(db, argument_id)
                for ident in ident_list:
                    varlist_in_condition.append(ident)
        # child_type == 'AndExpression' or child_type == 'OrExpression'(a == 0 || b != 0, &&)
        elif child_type == 'AndExpression' or child_type == 'OrExpression':
            node_list = get_child_type_for_AndOr(db, child_id)
            for node in node_list:
                varlist_in_condition = get_cv_for_AndOr(db,node)

        else:
            varlist_in_condition = condition_value_deliver(db, child_id)
    
    return varlist_in_condition

def sub_slice_backwards(startnode, all_nodes):

    predecessors = startnode.predecessors()
    startnode_loc = int(startnode['location'].split(':')[0])
    
    if predecessors != []:
        for p_node in predecessors:
            if p_node['location'] == None:
                    continue
            p_node_loc = int(p_node['location'].split(':')[0])
            if(p_node_loc > startnode_loc):
                continue
            if p_node in all_nodes:
                continue

            all_nodes.add(p_node)  
            sub_slice_backwards(p_node,all_nodes)


def program_slice_backwards(pdg,startNode):
    all_nodes = set()#记录切出的结点
    all_nodes.add(startNode)#加入出发点
    sub_slice_backwards(startNode,all_nodes)
    allnodesid=[]
    for node in all_nodes:
        allnodesid.append(node['name'])
    subgraph=pdg.subgraph(allnodesid)

    return subgraph


def sub_slice_forward(startnode,allnodes):

    successors = startnode.successors()
    startnode_loc = int(startnode['location'].split(':')[0])
    
    if successors != []:
        for p_node in successors:
            if p_node['location'] == None:
                    continue
            p_node_loc = int(p_node['location'].split(':')[0])
            if(p_node_loc < startnode_loc):
                continue
            if p_node in allnodes:
                continue
            allnodes.add(p_node)  
            sub_slice_forward(p_node,allnodes)



def program_slice_forward(pdg, list_startNode):         
    allnodes=set()
    allnodeid=[]
    for startNode in list_startNode:
            
        allnodes.add(startNode)#加入出发点
        if startNode['type']=='Function':
            continue
        sub_slice_forward(startNode,allnodes)

    for node in allnodes:
        allnodeid.append(node['name'])
    subgraph=pdg.subgraph(allnodeid)

    return subgraph



def get_all_identifiers_and_ptrArrMem_return_list(db, node_id):
    node_id = int(node_id)
    identifiers = []
    query_with_var = "g.v(%d).children()" % node_id
    children = db.runGremlinQuery(query_with_var)
    for child in children:
        node_id = child._id
        node_type = child['type']
        node_code = child['code']
        if node_type == "Identifier":
            identifiers.append(node_code)               
        else:
            if node_type == "PtrMemberAccess" or node_type == "ArrayIndexing" or node_type == 'MemberAccess':
                node_code.replace(" ","")
                identifiers.append(node_code)            
            q = Queue(maxsize=100)
            q.put(node_id)
            while not q.empty():
                node_id = q.get()
                query_with_var = "g.v(%d).children()" % node_id
                children = db.runGremlinQuery(query_with_var)
                for child in children:                        
                    child_type = child['type']
                    child_id = child._id
                    child_code = child['code'].replace(' ','')
                    if child_type == 'Identifier':
                        identifiers.append(child_code)
                    else:
                        if child_type == "PtrMemberAccess" or child_type == "ArrayIndexing" or child_type == 'MemberAccess':
                            identifiers.append(child_code)
                        q.put(child_id)


    identifiers = list(set(identifiers))
    return identifiers

def select_successors_for_condition(db, startnode):
    successors_all = startnode.successors()
    successors_all = list(set(successors_all))
    print('\n\t--------- succs of ',startnode['code'],'\t',startnode['location'])
    for suc in successors_all:
        print('\tall_succs:\t',suc['code'])

    condition_id = int(startnode['name'])
    startnode_line = startnode['location'].split(":")[0]
    successors_temp = []
    successors = []
    vars_in_cond_stmt = []

    query_with_var = "g.v(%d).parents()" % condition_id
    parents = db.runGremlinQuery(query_with_var)

    for res in parents:
        if res['type'] == 'ForStatement':
            forstmt_id = res._id
            var_in_forstmt = []

            query_with_var = "g.v(%d).children()" % forstmt_id
            children = db.runGremlinQuery(query_with_var)

            for child in children:
                child_type = child['type']
                child_id = child._id
                if child_type == 'ForInit' or child_type == "IncDecOp":
                    idents_in_forInit = []
                    idents_in_forInit = get_all_identifiers_and_ptrArrMem_return_list(db, child_id)
                    if idents_in_forInit != []:
                        for ident in idents_in_forInit:
                            var_in_forstmt.append(ident)
                
                elif child_type == 'Condition':
                    
                    var_in_condition = condition_value_deliver(db, child_id)
                    for var in var_in_condition:
                        var_in_forstmt.append(var)

                else:
                    continue
            
            vars_in_cond_stmt = list(set(var_in_forstmt))
        
        elif res['type'] == 'IfStatement':
            var_in_ifstmt = []
            query_with_var = "g.v(%d).children()" % res._id
            if_stmt_child = db.runGremlinQuery(query_with_var)
            for child in if_stmt_child:
                child_id = child._id
                child_type = child['type']
                varlist_in_condition = []
                if child_type == 'Condition':
                    var_in_condition = condition_value_deliver(db, child_id)
                    for var in var_in_condition:
                        var_in_ifstmt.append(var)
                break
            
            vars_in_cond_stmt = list(set(var_in_ifstmt))

        elif res['type'] == 'WhileStatement':
            var_in_whilestmt = []
            query_with_var = "g.v(%d).children()" % res._id
            while_stmt_child = db.runGremlinQuery(query_with_var)
            for child in while_stmt_child:
                child_id = child._id
                child_type = child['type']
                varlist_in_condition = []
                if child_type == 'Condition':
                    var_in_condition = condition_value_deliver(db, child_id)
                    for var in var_in_condition:
                        var_in_whilestmt.append(var)
                break
            
            vars_in_cond_stmt = list(set(var_in_whilestmt))

        elif res['type'] == 'SwitchStatement':
            return []              
                        
        else:
            successors_temp += successors_all

    for succ in successors_all:
        succ_id = succ['name']
        idents_in_succ = get_all_identifiers_and_ptrArrMem_return_list(db, succ_id)
        if vars_in_cond_stmt != []:
            for var in vars_in_cond_stmt:
                for ident in idents_in_succ:
                    if ident == var:
                        successors_temp.append(succ)
                        break
                    
    successors_temp = list(set(successors_temp))
    for node in successors_temp:
        line = node['location'].split(":")[0]
        if line > startnode_line:
            successors.append(node)

    if successors == []:
        print('-----------------------------------------------------------------------------------------------------------------------------------------')
        print("startnode: ",startnode['location'],"   HAS NO SUCCESSORS!","     startnode_id: ",condition_id)
        print('-----------------------------------------------------------------------------------------------------------------------------------------')
        return []

    else:
        for suc in successors:
            print('\tselected_succs:\t',suc['code'])
        return successors


def backward_to_decl(db, startnode, variable_name):
    #tarck backward dataflow to identifierDeclaration of the cirital variable 
    identifierDecl, variable_name = select_predecessors(db,startnode, variable_name)
    if identifierDecl == []:
        return [],[],variable_name
    startnode_new = identifierDecl[0]
    flag, successors = select_successors(db, startnode_new, variable_name)
    return identifierDecl, successors, variable_name

def select_predecessors(db, startnode, variable_name):
    identifierDecl = []
    predecessors = startnode.predecessors()

    query_with_var = "g.v(%d).parents().parents().parents()" % int(startnode['name'])
    parents = db.runGremlinQuery(query_with_var)

    if len(parents) == 1 and parents[0]['type'] == 'ForStatement':
        identifs = []
        query_with_var = "g.v(%d).children().children().children()" % int(parents[0]._id)
        identifiers = db.runGremlinQuery(query_with_var)
        for ident in identifiers:
            if ident['type'] == 'Identifier':
                identifs.append(ident['code'])

        for identi in identifs:
            if variable_name == identi:
                query_with_var = "g.v(%d).children()" % int(parents[0]._id)
                chilren = db.runGremlinQuery(query_with_var)
                for pre in predecessors:
                    for child in chilren:
                        if int(pre['name']) == child._id and pre['type'] == 'Condition':
                            return [pre],variable_name

    if "*" in variable_name:
        variable_name = variable_name.split("*")[-1]

    for p_node in predecessors:
        node_type = p_node['type']
        code = p_node['code']
        node_id = int(p_node['name'])
        idents_in_pre = get_all_identifiers_and_ptrArrMem_return_list(db, node_id)
        if node_type == 'IdentifierDeclStatement' or node_type == 'Parameter':
            if variable_name in idents_in_pre:
                identifierDecl.append(p_node)
    if identifierDecl == []:
        class_name = ''
        if "->" in variable_name:
            class_name = variable_name.split("->")[0]
            for p_node in predecessors:
                node_type = p_node['type']
                code = p_node['code']
                if node_type == 'IdentifierDeclStatement' or node_type == 'Parameter': 
                    if class_name in code:
                        identifierDecl.append(p_node)
                        variable_name = class_name
                        break

        elif "." in variable_name:
            class_name = variable_name.split(".")[0]
            for p_node in predecessors:
                node_type = p_node['type']
                code = p_node['code']
                if node_type == 'IdentifierDeclStatement' or node_type == 'Parameter':
                    if class_name in code:
                        identifierDecl.append(p_node)
                        variable_name = class_name
                        break

        else:
            print("NO PREDESSORS???")
            return [], variable_name

    if len(identifierDecl) != 1:
        print("The number of identifierdel ERRORS!!!")
    return identifierDecl, variable_name

def select_successors(db, startnode, variable_name):
    flag = 0
    #if the identifierDeclaration statement declares more than one variables
    #the successors of this node would include all variables' successors, so it has to be filtered
    successors_all = startnode.successors()
    successors_all = list(set(successors_all))
    print('\n\t------------- succs of ',startnode['code'],'\t',startnode['location'], '\tcv: '),  variable_name
    if successors_all == []:
        return flag, []
    for suc in successors_all:
        print('\tall_succs:\t',suc['code'], '\t', suc['location'])
    startnode_type = startnode["type"]
    startnode_line = startnode['location'].split(":")[0]
    startnode_code = startnode['code']
    successors_temp = []
    successors = []
    
    #declaration has wrong station that include more than one variable's successors
    #Startnode为identifierDeclStatement类型，并且该行定义了多个变量，e.g., int a,b,c 
    if startnode_type == "IdentifierDeclStatement" and ',' in startnode_code:
        # filter successors that are not related to the ciritical variable
        for succ_node in successors_all:
            succ_id = int(succ_node['name'])
            
            idents_in_succ = get_all_identifiers_and_ptrArrMem_return_list(db, succ_id)
            if idents_in_succ == []:
                successors_temp.append(succ_node)
            else:    
                for ident in idents_in_succ:
                    if ident == variable_name:
                        successors_temp.append(succ_node)
    elif startnode_type == "Condition":
        successors_temp = select_successors_for_condition(db, startnode)
        
    else:
        for succ_node in successors_all:
            succ_id = int(succ_node['name'])
            idents_in_succ = get_all_identifiers_and_ptrArrMem_return_list(db, succ_id)
            if variable_name in idents_in_succ:
                successors_temp.append(succ_node)

    for node in successors_temp:
        line = node['location'].split(":")[0]
        if line > startnode_line:
            successors.append(node)

    for suc in successors:
        print('\tselected_succs:\t',suc['code'], '\t', suc['location'])

    if successors == {}:
        flag = 1
        print("startnode: ",startnode['location'],"   HAS NO SUCCESSORS!")
        return flag,[]

    else:
        flag = 0    
        return flag, successors

def getCallnameandArg(node,j):
  if 'Statement' not in node['type']:
    return False
  query='g.v(%s).astNodes().filter{it.type==\"CallExpression\"}'%node['name']
  result=j.runGremlinQuery(query)
  
  if result==[]:
    return False
  else:
    call2args={}
    for node in result:
      argument_dict={}
      arglist=[]
      query='g.v(%d).astNodes().filter{it.type==\"Argument\"}'%node._id
      result=j.runGremlinQuery(query)
      if result==[]:
        continue
      for arg in result:
        argument_dict[arg['childNum']]=arg['code']
      for i in range(len(argument_dict)):
        arglist.append(argument_dict[str(i)])
      index= node['code'].find('(')
      callname=node['code'][:index].strip()
      call2args[callname]=arglist
    return call2args
# 向下跨函数,即跳到调用函数中切片
def process_cross_func(iter_times,current_time, testID, sub_graph,j):

    if iter_times == current_time:
        return sub_graph
    else:
        current_time +=1

    func_pointer_dict = {}
    path = os.path.join('dict_call2cfgNodeID_funcID', testID, 'func_pointer_dict.pkl')
    if os.path.exists(path):
        fin = open(path, 'rb')
        func_pointer_dict = pickle.load(fin)
        fin.close()

    for node in sub_graph.vs() :

        # ret = isNewOrDelOp(node, testID)
        # if ret:
        #     funcname = ret
        #     pdg = getFuncPDGByNameAndtestID(funcname, testID)              
            
        #     if pdg == False:
        #         not_scan_func_list.append(node['name'])
        #         continue
        #     else:
        #         # iter_time += 1
        #         result_list = sortedNodesByLoc(pdg.vs)
        #         not_scan_func_list.append(node['name'])
        #         index = 0
        #         for result_node in list_result_node:
        #             if result_node['name'] == node['name']:
        #                 break
        #             else:
        #                 index += 1
        #         # To Do 此处未增加边集----已增加 2022.9.22 wanghu
        #         for edge in pdg.es():
        #             list_edge.append((pdg.vs[edge.source]["name"], pdg.vs[edge.target]["name"]))

        #         _new_list = [result_list,iter_time]
        #         list_result_node = list_result_node[:index+1] + result_list + list_result_node[index+1:]
        #         list_result_node, list_edge = process_cross_func(_new_list, testID, slicetype, list_result_node, not_scan_func_list, list_edge)

        # else:          
        # ret = isFuncCall(node) #if funccall ,if so ,return funcnamelist
        
        ret=getCallnameandArg(node,j)
        if ret:
            in_edge_attr=set()
            for edge in node.in_edges():
                if edge['var']!=[]:
                    in_edge_attr.add(edge['var'])
            # print "isFuncCall: ",ret
            # iter_time += 1
            for funcname in ret.keys():
                arglist=ret[funcname]
                argindex=[]
                for i in range(len(arglist)):
                    for var in in_edge_attr:
                        if arglist[i]==var:
                            argindex.append(i)
                if argindex==[]:
                    continue
                funcname=str(funcname)
                if funcname in func_pointer_dict.keys():
                    funcname = func_pointer_dict[funcname]
                if funcname.find('->') != -1:
                    real_funcname = funcname.split('->')[-1].strip()
                    objectname = funcname.split('->')[0].strip()

                    funcID = node['functionId']
                    src_pdg = getFuncPDGByfuncIDAndtestID(funcID, testID)
                    if src_pdg == False:
                        continue
                        
                    for src_pnode in src_pdg.vs:
                        # if src_pnode['code'].find(objectname) != -1 and src_pnode['code'].find(' new ') != -1:
                        #     tempvalue = src_pnode['code'].split(' new ')[1].replace('*', '').strip()
                        tempvalue = ''
                        classname = ''
                        if src_pnode['code'].find(objectname) != -1 and src_pnode['type'] == 'IdentifierDeclStatement':
                            if '=' in src_pnode['code']:
                                if src_pnode['code'].find(' '+objectname+' = ') != -1:
                                    # print src_pnode['code'],objectname
                                    tempvalue = src_pnode['code'].split(' '+objectname+' = ')[1].replace('*', '').replace('new','').strip()
                            # else:
                            #     temp_value = src_pnode['code'].split(objectname)[0].replace('*', '').replace('&', '').strip()
                            if tempvalue.split(' ')[0] != 'const':
                                classname = tempvalue.split(' ')[0]
                            else:
                                classname = tempvalue.split(' ')[1]
                        elif src_pnode['code'].find(objectname) != -1 and src_pnode['type'] == 'Parameter':
                            classname = src_pnode['code'].split(' ')[0].replace('*', '').replace('&','').strip()
                            
                        if classname != '':
                            # print objectname,classname
                            break

                    if classname == '':
                        continue

                    funcname = classname + ' :: ' + real_funcname
                    # pdg,func_id = getFuncPDGByNameAndtestID(funcname, testID)


                elif funcname.find('.') != -1:
                    real_funcname = funcname.split('.')[-1].strip()
                    objectname = funcname.split('.')[0].strip()

                    funcID = node['functionId']
                    src_pdg = getFuncPDGByfuncIDAndtestID(funcID, testID)
                    if src_pdg == False:
                        continue
                    for src_pnode in src_pdg.vs:
                        # if src_pnode['code'].find(objectname) != -1 and src_pnode['code'].find(' new ') != -1:
                        #     tempvalue = src_pnode['code'].split(' new ')[1].replace('*', '').strip()
                        tempvalue = ''
                        classname = ''
                        if src_pnode['code'].find(objectname) != -1 and src_pnode['type'] == 'IdentifierDeclStatement':
                            if '=' in src_pnode['code']:
                                if src_pnode['code'].find(' '+objectname+' = ') != -1:
                                    tempvalue = src_pnode['code'].split(' '+objectname+' = ')[1].replace('*', '').replace('new','').strip()
                            # else:
                            #     temp_value = src_pnode['code'].split(objectname)[0].replace('*', '').replace('&', '').strip()
                            if tempvalue.split(' ')[0] != 'const':
                                classname = tempvalue.split(' ')[0]
                            else:
                                classname = tempvalue.split(' ')[1]
                        elif src_pnode['code'].find(objectname) != -1 and src_pnode['type'] == 'Parameter':
                            classname = src_pnode['code'].split(' ')[0].replace('*', '').replace('&','').strip()
                            
                        if classname != '':
                            # print objectname,classname
                            break

                    if classname == '':
                        continue

                    funcname = classname + ' :: ' + real_funcname
                    # pdg,func_id = getFuncPDGByNameAndtestID(funcname, testID)

                # else:
                pdg,func_id = getFuncPDGByNameAndtestID(funcname, testID)

                if pdg == False:  
                    continue

                else:
                    param_node = []
                    FuncEntryNode = False
                    for vertex in pdg.vs:#分别找到参数节点和函数入口节点
                        if vertex['type'] == 'Parameter':
                            param_node.append(vertex)
                        elif vertex['type'] == 'Function':
          
                            FuncEntryNode = vertex
                    
                    if not FuncEntryNode or param_node == []:#没有Fuction节点，Joern解析出错；没有参数，认为无数据流传递
                        # not_scan_func_list.add(node['name'])
                        continue

                    else:
                        param_node=sortedNodesByLoc(param_node)
                        startnodes=[FuncEntryNode]
                        for index in argindex:
                            startnodes.append(param_node[index])
                        sub_graph_for = program_slice_forward(pdg, startnodes)#从参数向下切片

                        sub_graph_cross = process_cross_func(iter_times,current_time, testID, sub_graph_for,j)
                        sub_graph=sub_graph.union(sub_graph_cross)
                        sub_graph.add_edge(node['name'],FuncEntryNode['name'])

                        
    return sub_graph

#向下跨函数，即调到调用当前函数的函数返回值后的语句开始切片
# def process_return_back(list_tuple_results_back, testID, i, not_scan_func_list, list_edge):
#     while i < len(list_tuple_results_back):
#         iter_list_edge = list_edge[i]
#         iter_time = list_tuple_results_back[i][1]
#         if iter_time == 3 or iter_time == -1:   # allow cross 3 funcs
#             i += 1
#             continue

#         else:
#             list_node = list_tuple_results_back[i][0]

#             if list_node == []:
#                 i += 1
#                 continue

#             func_id = list_node[-1]['functionId']
#             path = os.path.join('dict_call2cfgNodeID_funcID', testID, 'dict.pkl')
#             if not os.path.exists(path):
#                 i += 1
#                 continue
#             fin = open(path, 'rb')
#             _dict = pickle.load(fin)
#             fin.close()
                
#             if func_id not in _dict.keys():
#                 list_tuple_results_back[i][1] = -1
#                 i += 1
#                 continue

#             else:                
#                 list_cfgNodeID = _dict[func_id]
#                 dict_func_pdg = getFuncPDGBynodeIDAndtestID(list_cfgNodeID, testID)
#                 iter_time += 1
#                 _new_list = []
#                 _new_edge = []
#                 for item in dict_func_pdg.items():
#                     targetPDG = item[1]
#                     startnode = []
#                     ret_edges = []
#                     for n in targetPDG.vs:
#                         if n['name'] == item[0]:#is id
#                             startnode = [n]
#                             # ret_edges = [(n['functionId'],func_id)]
#                             ret_edges = [(list_node[-1]['name'],n['name'])]
#                             break
                        
#                     if startnode == []:
#                         continue
#                     if startnode[0]['name'] in not_scan_func_list:
#                         continue
#                     # ret_list_backwards, ret_edges_backwards = program_slice_backwards(targetPDG, startnode, ret_edges)
#                     ret_list_forwards, ret_edges_forwards = program_slice_forward(targetPDG, startnode, ret_edges)
#                     not_scan_func_list.append(startnode[0]['name'])

#                     if ret_list_forwards == [] or len(ret_list_forwards) == 1:
#                         continue

#                     # ret_list = ret_list_backwards + list_node + ret_list_forwards
#                     # ret_edges = ret_edges_backwards + iter_list_edge + ret_edges_forwards
#                     ret_list = list_node + ret_list_forwards
#                     ret_edges = iter_list_edge + ret_edges_forwards
#                     _new_list.append([ret_list, iter_time])
#                     _new_edge.append(ret_edges)

#                 if _new_list != []:
#                     del list_tuple_results_back[i]
#                     list_tuple_results_back = list_tuple_results_back + _new_list
#                     del list_edge[i]
#                     list_edge = list_edge + _new_edge
#                     list_tuple_results_back, list_edge = process_return_back(list_tuple_results_back, testID, i, not_scan_func_list, list_edge)
#                 else:
#                     list_tuple_results_back[i][1] = -1
#                     i += 1
#                     continue
                   
#     return list_tuple_results_back, list_edge

#向下跨函数，即到调用当前函数的函数返回值后的语句开始切片 调整为和process crocc func类似的处理方式 2022.9.23 wanghu

def process_return_back(iter_times_retback,current_time_retback,lastnode,funcid,subgraph,testID,funcnum,j):


    if iter_times_retback == current_time_retback:
        return [subgraph]
    else:
        current_time_retback +=1

    path = os.path.join('dict_call2cfgNodeID_funcID', testID, 'dict.pkl')
    if not os.path.exists(path):
        return [subgraph]
    fin = open(path, 'rb')
    _dict = pickle.load(fin)#function->call
    fin.close()
        
    if funcid not in _dict.keys():
        return [subgraph]

    
    else: 
        graph_list=[]               
        list_cfgNodeID = _dict[funcid]
        dict_func_pdg = getFuncPDGBynodeIDAndtestID(list_cfgNodeID, testID)

        for item in dict_func_pdg.items()[:funcnum]:
            targetPDG = item[1]
            startnodes = []

            for n in targetPDG.vs:
                if n['name'] == item[0]:#is callid
                    startnodes = [n]
                    break
                
            if startnodes == []:
                continue

            subgraph_for = program_slice_forward(targetPDG, startnodes)
            subgraph_cross=process_cross_func(0,0,testID,subgraph_for,j)#暂时将跨函数层数设为0表示不跨,降低复杂度

            new_funcid=startnodes[0]['functionId']
            new_lastnode=sortedNodesByLoc(subgraph_for.vs())[-1]
            subgraph_list=process_return_back(iter_times_retback,current_time_retback,new_lastnode,new_funcid,subgraph_cross,testID,funcnum,j)
            
            for subgraph1 in subgraph_list:
                new_graph=subgraph.union(subgraph1)
                new_graph.add_edge(lastnode['name'],startnodes[0]['name'])
                graph_list.append(new_graph)

            
    return graph_list
