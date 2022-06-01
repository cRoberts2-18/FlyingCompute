from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from threading import Lock
import os
from numpy import broadcast
import pandas as pd
import csv
import random
import json
import shutil
import MultiPath

class drone:
  def __init__(self,sID,charge,coord,path):
    self.sID=sID
    self.charge=charge
    self.coord=coord
  def pathcompute(self,teams):
    dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
    path = os.path.join(dir, str(self.sID))
    edges=os.path.join(path,"edgelist.csv")
    nodes=os.path.join(path,"nodelist.csv")
    pathings=MultiPath.pathCompute(int(teams),nodes,edges)
    self.charge-=10
    return(pathings)
    
drone1=drone(0,100,[250,250],"")
drone2=drone(0,100,[250,750],"")
drone3=drone(0,100,[750,750],"")
drone4=drone(0,100,[750,250],"")

def recompute(x,key):
  dict={'charge1':drone1.charge,'charge2':drone2.charge,'charge3':drone3.charge,'charge4':drone4.charge}
  maxcharge=max(dict, key=dict.get)
  if maxcharge=='charge1':
    pathing=drone1.pathcompute(x)
  elif maxcharge=='charge2':
    pathing=drone2.pathcompute(x)
  elif maxcharge=='charge3':
    pathing=drone3.pathcompute(x)
  elif maxcharge=='charge4':
    pathing=drone4.pathcompute(x)
  
  dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
  path = os.path.join(dir, str(key))
  pathList=os.path.join(path,"path.txt")
  f=open(pathList,"w")
  for i in range(1,len(pathing)+1):
    f.write(str(pathing[i])+"\n")
  f.close()
  
  return(pathing)
    
#intial setup for the flask system
app= Flask(__name__, template_folder='Templates')
app.secret_key="flyboy"
async_mode=None
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

#each app route method refers to either a page that can viewed or a backend function 
@app.route('/')
def home():
  return render_template('base.html')

@app.route('/search/')
def search():
  return render_template('Search.html')

@app.route('/BeginSearch/', methods = ['GET', 'POST'])
def beginSearch():
  key=random.randint(1000000,9999999)
  nodeArray=[]
  edgeArray=[]
  nodes=json.loads(request.values.get("nodes"))
  edges=json.loads(request.values.get("edges"))
  teams=request.values.get("teams")
  name=request.values.get("name")
  age=request.values.get("age")
  for i in range(0,len(nodes)):
    tempArray=[]
    tempArray.append(nodes[i]['id'])
    tempArray.append(nodes[i]['X'])
    tempArray.append(nodes[i]['Y\r'])
    nodeArray.append(tempArray)
  for i in range(0,len(edges)):
    tempArray=[]
    tempArray.append(edges[i]['node1'])
    tempArray.append(edges[i]['node2'])
    tempArray.append(edges[i]['trail'])
    tempArray.append(edges[i]['distance'])
    tempArray.append(edges[i]['color'])
    tempArray.append(edges[i]['estimate\r'])
    edgeArray.append(tempArray)
  for i in range(0,len(nodeArray)):
    nodeArray[i][len(nodeArray[i])-1]=nodeArray[i][len(nodeArray[i])-1].replace("\r","")
  for i in range(0,len(edgeArray)):
    edgeArray[i][len(edgeArray[i])-1]=edgeArray[i][len(edgeArray[i])-1].replace("\r","")
  
  dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
  path = os.path.join(dir, str(key))
  os.mkdir(path)
  edgeLocation=os.path.join(path,"edgelist.csv")
  nodeLocation=os.path.join(path,"nodelist.csv")
  edges = pd.DataFrame(edgeArray, columns=['node1', 'node2','trail','distance','color','estimate'])
  edges.to_csv(edgeLocation)
  nodes = pd.DataFrame(nodeArray, columns=['id', 'X','Y'])
  nodes.to_csv(nodeLocation)
  info=os.path.join(path,"info.txt")
  f = open(info, "w")
  writestr=name+","+age
  f.write(writestr)
  f.close()
  
  drone1.sID=key
  drone2.sID=key
  drone3.sID=key
  drone4.sID=key

  pathing=drone1.pathcompute(teams)
  pathList=os.path.join(path,"path.txt")
  f=open(pathList,"w")
  for i in range(1,len(pathing)+1):
    f.write(str(pathing[i])+"\n")
  f.close()
  return({"key":key,"path":pathing})


@app.route('/endSearch/', methods = ['GET', 'POST'])
def endSearch():
  drone1.sID=0
  drone2.sID=0
  drone3.sID=0
  drone4.sID=0
  key=request.values.get("key")
  dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
  path = os.path.join(dir, str(key))
  shutil.rmtree(path)
  return("")
@app.route('/connectSearch/', methods = ['GET','POST'])
def connectSearch():
  key = request.values.get('key')
  pathArr=[]
  dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
  path = os.path.join(dir, str(key))
  isPath=os.path.isdir(path)
  
  if isPath==True:
    info=""
    infoList=os.path.join(path,"info.txt")
    f = open(infoList, "r")
    for x in f:
      info=x
    pathList=os.path.join(path,"path.txt")
    f = open(pathList, "r")
    pathDict={}
    for x in f:
      pathArr.append(x.replace("[","").replace("]","").replace(" ","").replace("\n","").replace("'","").replace("),(","!").replace("(","").replace(")",""))
    for i in range(0,len(pathArr)):
      tempArr=pathArr[i].split("!")
      tupleArr=[]
      for j in range(0,len(tempArr)):
          tupleArr.append(tempArr[j].split(","))
      pathDict[i]=tupleArr
      returnDict={"0":info,"1":pathDict}
  else:
    returnDict="False"
  return(returnDict)

@socketio.on('test_message')
def handle_message(data):
    print('received message: ' + str(data))
    emit('test_response', {'data': 'Test response sent'})

@socketio.on('end_search')
def handle_message(data):
    print('received message: ' + str(data))
    emit('search_over', {'data': 'Search Concluded'}, broadcast=True)

@socketio.on('user_connect')
def handle_message(data):
    print('received message: ' + str(data))
    emit('update_connect', {'data': str(data)}, broadcast=True)

@socketio.on('location_update')
def handle_message(data):
    print('received message: ' + str(data))
    nodes=data['edge'].split(",")
    dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
    path = os.path.join(dir, str(data['key']))
    file=os.path.join(path, "edgelist.csv")
    df = pd.read_csv(file)
    df.loc[df.index[(df['node1']==nodes[0]) & (df['node2']==nodes[1])],'estimate']+=data['checked']
    df.loc[df.index[(df['node2']==nodes[0]) & (df['node1']==nodes[1])],'estimate']+=data['checked']
    df.to_csv(file,index=False)
   

@socketio.on('blocked_path')
def handle_message(data):
    block="Block encountered at: "+data['data']
    dir=("C:\\Users\\callu\\Desktop\\21COD290 - Thesis Project\\FlaskApp\\static\\Searches")
    path = os.path.join(dir, str(data['key']))
    file=os.path.join(path, "edgelist.csv")
    df = pd.read_csv(file)
    nodes=data['data'].split(",")
    df.drop(df.index[(df['node1']==nodes[0]) & (df['node2']==nodes[1])],axis=0,inplace=True)
    df.drop(df.index[(df['node2']==nodes[0]) & (df['node1']==nodes[1])],axis=0,inplace=True)
    df.to_csv(file,index=False)
    pathing=recompute(data['team'],data['key'])
    print(pathing)
    emit('confirm_block', {'block':block,'path':pathing}, broadcast=True)
    pathList=os.path.join(path,"path.txt")
    f = open(pathList, "r")
    pathArr=[]
    pathDict={}
    for x in f:
      pathArr.append(x.replace("[","").replace("]","").replace(" ","").replace("\n","").replace("'","").replace("),(","!").replace("(","").replace(")",""))
    for i in range(0,len(pathArr)):
      tempArr=pathArr[i].split("!")
      tupleArr=[]
      for j in range(0,len(tempArr)):
          tupleArr.append(tempArr[j].split(","))
      pathDict[i]=tupleArr
    emit('new_pathing', {'path':pathDict}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
