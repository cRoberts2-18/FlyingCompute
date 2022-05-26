rom flask import Flask, render_template, request, redirect, url_for, session
import os 


#intial setup for the flask system
app= Flask(__name__)
app.secret_key="flyboy"

#each app route method refers to either a page that can viewed or a backend function 
@app.route('/')
def home():
  return render_template('base.html')
