from flask import Flask, render_template, request, redirect, url_for, session
import os
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
    dir=("/home/ubuntu/search")
    path = os.path.join(dir, str(self.sID))
    edges=os.path.join(path,"edgelist.csv")
    nodes=os.path.join(path,"nodelist.csv")
    pathings=MultiPath.pathCompute(int(teams),nodes,edges)
    self.charge-=10;
    return(pathings)
    
drone1=drone(0,100,[250,250],"")
drone2=drone(0,100,[250,750],"")
drone3=drone(0,100,[750,750],"")
drone4=drone(0,100,[750,250],"")


    
#intial setup for the flask system
app= Flask(__name__, template_folder='Templates')
app.secret_key="flyboy"

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
  
  dir=("/home/ubuntu/search")
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
  dir=("/home/ubuntu/search")
  path = os.path.join(dir, str(key))
  shutil.rmtree(path)
  return("")
@app.route('/connectSearch/', methods = ['GET','POST'])
def connectSearch():
  key = request.values.get('key')
  pathArr=[]
  dir=("/home/ubuntu/search")
  path = os.path.join(dir, str(key))
  isPath=os.path.isdir(path)
  
  if isPath==True:
    info=[]
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
