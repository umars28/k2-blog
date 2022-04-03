from flask import Flask, render_template
from flask_bootstrap import Bootstrap4
from pymongo import MongoClient
from flask_pymongo import PyMongo

app = Flask(__name__)
bootstrap = Bootstrap4(app)
app.config['MONGO_DBNAME'] = 'blog'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false'

mongo = PyMongo(app)
# client = MongoClient('localhost', 27017)
# db = client.mydb

@app.route('/auth/login')
def login():
    return render_template('Auth/login.html')

@app.route('/auth/register')
def register():
    return render_template('Auth/register.html')    

@app.route('/')
def homepage():
    return render_template('FE/index.html')

@app.route('/detail')
def detail():
    return render_template('FE/detail.html')

@app.route('/list')
def list():
    return render_template('FE/list.html')   

@app.route('/admin/dashboard')
def adminDashboard():
    return render_template('CMS/dashboard/dashboard.html')

@app.route('/admin/category/index')
def adminCategoryIndex():
    return render_template('CMS/category/index.html')

@app.route('/admin/category/create')
def adminCategoryCreate():
    return render_template('CMS/category/create.html')  

@app.route('/admin/tag/index')
def adminTagIndex():
    return render_template('CMS/tags/index.html')

@app.route('/admin/tag/create')
def adminTagCreate():
    return render_template('CMS/tags/create.html')        
    
@app.route('/admin/manage/index')
def adminManageIndex():
    return render_template('CMS/admin/index.html')

@app.route('/admin/manage/create')
def adminManageCreate():
    return render_template('CMS/admin/create.html')  

@app.route('/admin/user/index')
def adminUserIndex():
    return render_template('CMS/user/index.html')

@app.route('/admin/user/create')
def adminUserCreate():
    return render_template('CMS/user/create.html') 

if __name__ == '__main__':
    app.run()