from __future__ import print_function
from joern.all import JoernSteps
import re

def getCallnameandArg(node,j):
  if 'Statement' not in node['type']:
    return False
  query='g.v(%d).astNodes().filter{it.type==\"CallExpression\"}'%node['name']
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
      callname=node['code'][:index]
      call2args[callname]=arglist
    # print(call2args)
def inc(a):
  a=a+1
  print(a)


if __name__=="__main__":
  j = JoernSteps()
  j.connectToDatabase()
  # node={
  #   'type':'Statement',
  #   'name':124
  # }
  # getCallnameandArg(node,j)
  query = 'queryNodeIndex("type:IdentifierDeclStatement")' #查询标识符
  list_arrays_node=[]
  results = j.runGremlinQuery(query)
  if results != []:
          for re in results:
              code = re.properties['code']
              if code.find(' = ') != -1:
                  code = code.split(' = ')[0]

              if code.find(' [ ') != -1:   #数组匹配
                  list_arrays_node.append(re)
  print(list_arrays_node)
    
  # a=0
  # inc(a)
  # print(a)