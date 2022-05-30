from flask import Flask, render_template, request, redirect, url_for, session
import os
import pandas as pd
import csv
import random
import json
import shutil
import MultiPath

class drone:
  def __init__(self,sID,charge,coord,path,teams):
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
    
drone1=drone(0,100,[250,250],"","")
drone2=drone(0,100,[250,750],"","")
drone3=drone(0,100,[750,750],"","")
drone4=drone(0,100,[750,250],"","")
  

    
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
  
  drone1.sID=key
  drone2.sID=key
  drone3.sID=key
  drone4.sID=key
  drone1.teams=teams
  drone2.teams=teams
  drone3.teams=teams
  drone4.teams=teams
  pathing=drone1.pathcompute(teams)
  drone1.path=pathing
  drone2.path=pathing
  drone3.path=pathing
  drone4.path=pathing
  return({"key":key,"path":pathing})


@app.route('/endSearch/', methods = ['GET', 'POST'])
def endSearch():
  drone1.sID=0
  drone2.sID=0
  drone3.sID=0
  drone4.sID=0
  drone1.teams=""
  drone2.teams=""
  drone3.teams=""
  drone4.teams=""
  drone1.path=""
  drone2.path=""
  drone3.path=""
  drone4.path=""
  key=request.values.get("key")
  dir=("/home/ubuntu/search")
  path = os.path.join(dir, str(key))
  shutil.rmtree(path)
  return("")
@app.route('/connectSearch/', methods = ['GET','POST'])
def connectSearch():
  key = request.values.get('key')
  if key==str(drone1.sID):
    path=drone1.path
  else
    path="False"
  return(path)
