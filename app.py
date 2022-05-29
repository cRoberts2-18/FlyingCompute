from flask import Flask, render_template, request, redirect, url_for, session
import os
import random
import json

class drone:
  def __init__(self,name, charge,coord):
    self.name=name
    self.charge=charge
    self.coord=coord
    


#intial setup for the flask system
app= Flask(__name__, template_folder='Templates')
app.secret_key="flyboy"

#each app route method refers to either a page that can viewed or a backend function 
@app.route('/')
def home():
  return render_template('base.html')

@app.route('/BeginSearch/', methods = ['GET', 'POST'])
def beginSearch():
  key=random.randint(1000000,9999999)
  nodeArray=[]
  edgeArray=[]
  nodes=json.loads(request.values.get("nodes"))
  edges=json.loads(request.values.get("edges"))
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
  return(str(key))
@app.route('/endSearch/', methods = ['GET', 'POST'])
def endSearch():
  key=request.values.get("key")
  dir=("/home/ubuntu/search")
  path = os.path.join(dir, str(key))
  os.rmdir(path)
  return("")
