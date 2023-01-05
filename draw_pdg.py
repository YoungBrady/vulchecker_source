import pickle
import graphviz
import os
import igraph
import sys
if __name__=='__main__':
    pdg_path='/home/lyl/huawei_project/slice_all/NVD/CWE-119/0/ffmpegCVE-2011-3929/new/pdg_db/new/avpriv_dv_produce_packet_1777'
    with open(pdg_path,'rb')as f:
        pdg=pickle.load(f)

    g=graphviz.Digraph(format='pdf')
    for node in pdg.vs():

        g.node(node['name'],node['code']+'\n'+node['location'].split(':')[0])
    for edge in pdg.es():
        g.edge(edge.source_vertex['name'],edge.target_vertex['name'],edge['var'])
    g.render('pdg',view=False)
