from flask import Flask, render_template, request, redirect, url_for, session
import os 

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
  nodes=request.values.get("nodeArray")
  edges=request.values.get("edgeArray")
  return("".join(str(x) for x in nodes))
