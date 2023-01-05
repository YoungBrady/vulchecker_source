import pickle
import graphviz
import os
import igraph
import sys
if __name__=='__main__':
    type=sys.argv[1]
    # type='old'
    if type =='old':
         with open('/home/lyl/huawei_project/code/pkl/CWE-119_old.pkl','rb')as f:
            label_dict=pickle.load(f)
    else:
        with open('/home/lyl/huawei_project/code/pkl/CWE-119_new.pkl','rb')as f:
            label_dict=pickle.load(f)
    for graph in os.listdir('./slice_graph'):
        fileID=graph.split('@@')[0]
        if fileID[:-8] not in label_dict:
            continue
        with open('./slice_graph'+'/'+graph,'rb')as f:
            slice_graph=pickle.load(f)
        flag=False
        g=graphviz.Digraph(graph[:-4]+'.png')
        for node in slice_graph.vs():
            loc=node['location'].split(':')[0]
            if int(loc) in label_dict[fileID[:-8]]:
                flag=True
            g.node(node['name'],node['code']+'\n'+node['location'].split(':')[0])
        for edge in slice_graph.es():
            g.edge(edge.source_vertex['name'],edge.target_vertex['name'],edge['var'])
        if flag:
            g.render('./image/'+graph[:-4]+'.png',view=False)
