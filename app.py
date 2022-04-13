from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap4
from pymongo import MongoClient
from flask_pymongo import PyMongo
from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from markupsafe import escape
from var_dump import var_dump
#from flask_bcrypt import Bcrypt
import bcrypt
import os

client = MongoClient("mongodb://127.0.0.1:27017") #host uri
dbs = client.blog    #Select the database



db = MongoEngine()
app = Flask(__name__)
bootstrap = Bootstrap4(app)
app.config['MONGO_DBNAME'] = 'blog'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false'

mongo = PyMongo(app)
client = MongoClient('localhost', 27017)
db_2 = client.get_database('blog')
user_record = db_2.users
article_record = db_2.articles


app.config['MONGODB_SETTINGS'] = {
    'host':'mongodb://localhost/blog'
}

app.config['SECRET_KEY'] = 'inikuncirahasiasaya'

app.config['UPLOAD_FOLDER'] = 'static/image_upload'

db.init_app(app)

class Category(db.Document):
    name = db.StringField(required=True)
    status = db.StringField(max_length=50)

CategoryForm = model_form(Category)

class Users(db.Document):
    username = db.StringField(required=True)
    first_name = db.StringField(required=True)
    last_name = db.StringField()
    role = db.StringField()
    password = db.StringField()
    status = db.StringField(max_length=50)

UserForm = model_form(Users)
    
class Articles(db.Document):
    title = db.StringField(required=True)
    banner = db.StringField()
    category = db.StringField(required=True)
    tag = db.StringField(required=True)
    description = db.StringField(required=True)
    writer = db.StringField()
    published_date = db.StringField()
    status = db.StringField()

ArticleForm = model_form(Articles)

@app.route('/auth/login', methods =['GET', 'POST'])
def login():
    message = ''
    if "username" in session:
        return redirect(url_for("adminDashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

       
        username_found = user_record.find_one({"username": username})
        if username_found:
            username_val = username_found['username']
            passwordcheck = username_found['password']
            
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["username"] = username_val
                return redirect(url_for('adminDashboard'))
            else:
                if "username" in session:
                    return redirect(url_for("adminDashboard"))
                message = 'Wrong password'
                return render_template('Auth/login.html', message=message)
        else:
            message = 'Username not found'
            return render_template('Auth/login.html', message=message)
    return render_template('Auth/login.html', message=message)
  
@app.route('/auth/register', methods =['GET', 'POST'])
def register():
    message = ''
    if "username" in session:
        return redirect(url_for("homepage"))
    if request.method == "POST":
        username = request.form.get("username")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        
        password1 = request.form.get("password")
        password2 = request.form.get("password-confirm")
        
        user_found = user_record.find_one({"username": username})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('Auth/register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('Auth/register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'username': username, 'first_name': first_name, 'last_name': last_name, 'role': 'REGULER', 'status': 'INACTIVE', 'password': hashed}
            user_record.insert_one(user_input)
            session["username"] = username
            return redirect(url_for('adminDashboard'))
   
    return render_template('Auth/register.html')

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
      

@app.route('/')
def homepage():
    data = Articles.objects(id='6255b21cc839d7184a0ad22b').first()
    form = ArticleForm(obj = data)

    articles_most_read = dbs.articles.find()

    return render_template('FE/index.html', form=form, articles=articles_most_read)

@app.route('/detail/<title>')
def detail(title):
    data = Articles.objects(title=title).first()
    
    form = ArticleForm(obj = data)
    return render_template('FE/detail.html', form=form)

@app.route('/list')
def list():
    return render_template('FE/list.html')   

@app.route('/admin/dashboard')
def adminDashboard():
    if session.get('username') == None:
        return redirect(url_for('login'))
    category_count = dbs.category.count_documents({})
    user_count = dbs.users.count_documents({})
    article_count = dbs.articles.count_documents({})
    return render_template('CMS/dashboard/dashboard.html', category_count=category_count, user_count=user_count, article_count=article_count)


# ADMIN CATEGORY
@app.route('/admin/category/index')
def adminCategoryIndex():
    if session.get('username') == None:
        return redirect(url_for('login'))
    categories = dbs.category.find()
    data = Users.objects(username=session["username"]).first()
    
    username = UserForm(obj = data)
    #categories = Category.objects()
#    categories = Category.objects()
    return render_template('CMS/category/index.html', categories=categories, username=username)

@app.route('/admin/category/create', methods=['GET'])
def adminCategoryCreate():
    if session.get('username') == None:
        return redirect(url_for('login'))
    form = CategoryForm()
    return render_template('CMS/category/create.html', form=form)  

@app.route('/admin/category/save', methods=['POST'])
def adminCategorySave():
    if session.get('username') == None:
        return redirect(url_for('login'))
    form = CategoryForm()
    data = form.data
    del data['csrf_token']
    save = Category(**data).save()
    flash('Berhasil disimpan!')
    return redirect(url_for('adminCategoryIndex')) 

@app.route('/admin/category/delete/<id>')
def adminCategoryDelete(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    Category.objects(id=id).delete()
    flash('Berhasil dihapus!')
    return redirect(url_for('adminCategoryIndex')) 

@app.route('/admin/category/edit/<id>')
def adminCategoryEdit(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    data = Category.objects(id=id).first()
    
    form = CategoryForm(obj = data)
    var_dump(form)
    return render_template('/CMS/category/edit.html', form=form, id=id)

@app.route('/admin/category/update/<id>', methods=['POST'])
def adminCategoryUpdate(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    form = CategoryForm()
    data = form.data
    del data['csrf_token']
    save = Category.objects(id=id).update(**data)
    flash('Berhasil diupdate!')
    return redirect(url_for('adminCategoryIndex')) 
# END OF ADMIN CATEGORY


# ADMIN USER
@app.route('/admin/user/index')
def adminUserIndex():
    if session.get('username') == None:
        return redirect(url_for('login'))
    users = dbs.users.find()
    data = Users.objects(username=session["username"]).first()
    
    username = UserForm(obj = data)
    return render_template('CMS/user/index.html', users=users, username=username)

@app.route('/admin/user/create', methods=['GET'])
def adminUserCreate():
    if session.get('username') == None:
        return redirect(url_for('login'))
    form = UserForm()
    return render_template('CMS/user/create.html', form=form) 

@app.route('/admin/user/save', methods=['POST'])
def adminUserSave():
    if session.get('username') == None:
        return redirect(url_for('login'))
    hashed = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
    user_input = {
            'username': request.form.get('username'), 
            'first_name': request.form.get('first_name'), 
            'last_name': request.form.get('last_name'),
            'role': request.form.get('role'),
            'status': request.form.get('status'),
            'password': hashed
        }
    user_record.insert_one(user_input)

#     user = dbs.users
#     user.username= request.form.get('username')
#     user.first_name= request.form.get('first_name')
#     user.last_name= request.form.get('last_name')
#     user.role= request.form.get('role')
#     # salt = bcrypt.gensalt()
#     # user.password = bcrypt.hashpw(request.form.get('password').encode('utf8'), salt)
#     pwhash = bcrypt.hashpw(request.form.get('password').encode('utf8'), bcrypt.gensalt())
#     user.password = pwhash.decode('utf8') # decode the hash to prevent is encoded twice
#    # user.password= bcrypt.generate_password_hash(request.form.get('password').encode('utf-8'))
#     user.status =request.form.get('status')
#     #user.validate()
#     user.save()
    flash('Berhasil disimpan!')
    return redirect(url_for('adminUserIndex'))

@app.route('/admin/user/delete/<id>')
def adminUserDelete(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    Users.objects(id=id).delete()
    flash('Berhasil dihapus!')
    return redirect(url_for('adminUserIndex')) 

@app.route('/admin/user/edit/<id>')
def adminUserEdit(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    data = Users.objects(id=id).first()
    
    form = UserForm(obj = data)
    var_dump(form)
    return render_template('/CMS/user/edit.html', form=form, id=id)

@app.route('/admin/user/update/<username>', methods=['POST'])
def adminUserUpdate(username):
    if session.get('username') == None:
        return redirect(url_for('login'))
    hashed = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
    if request.form.get('password'):
        myquery = { "username": username }
        newvalues = { "$set": { 
                    'username': request.form.get('username'), 
                    'first_name': request.form.get('first_name'), 
                    'last_name': request.form.get('last_name'),
                    'role': request.form.get('role'),
                    'status': request.form.get('status'),
                    'password': hashed
                } 
            }
        user_record.update_one(myquery, newvalues)
    else:
        myquery = { "username": username }
        newvalues = { "$set": { 
                    'username': request.form.get('username'), 
                    'first_name': request.form.get('first_name'), 
                    'last_name': request.form.get('last_name'),
                    'role': request.form.get('role'),
                    'status': request.form.get('status'),
                } 
            }
        user_record.update_one(myquery, newvalues)
    #username_found = user_record.find_one({"username": username})
    #var_dump(username_found)
    # user.username= request.form.get('username')
    # user.first_name= request.form.get('first_name')
    # user.last_name= request.form.get('last_name')
    # user.role= request.form.get('role')
    # if request.form.get('password'):
    #     user.password= bcrypt.generate_password_hash(request.form.get('password').encode('utf-8'))
    # user.status =request.form.get('status')
    # user.validate()
    # user.save()       
                       
    flash('Berhasil diupdate!')
    return redirect(url_for('adminUserIndex')) 
# END OF ADMIN USER


# ADMIN ARTICLE
@app.route('/admin/article/index')
def adminArticleIndex():
    if session.get('username') == None:
        return redirect(url_for('login'))
    articles = dbs.articles.find()
    data = Users.objects(username=session["username"]).first()
    
    username = UserForm(obj = data)
    return render_template('CMS/article/index.html', articles=articles, username=username)

@app.route('/admin/article/create', methods=['GET'])
def adminArticleCreate():
    if session.get('username') == None:
        return redirect(url_for('login'))
    categories = dbs.category.find()
    form = ArticleForm()
    return render_template('CMS/article/create.html', form=form, categories=categories) 

@app.route('/admin/article/save', methods=['POST'])
def adminArticleSave():
    if session.get('username') == None:
        return redirect(url_for('login'))
    article_input = {
            'title': request.form.get('title'), 
            'category': request.form.get('category'), 
            'tag': request.form.get('tag'),
            'banner': request.files['banner'].filename,
            'description': request.form.get('description'),
            'writer': session["username"],
            'published_date': request.form.get('published_date'),
            'status': request.form.get('status')
        }
    article_record.insert_one(article_input)
    if request.files['banner']:
        file = request.files['banner']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

    flash('Berhasil disimpan!')
    return redirect(url_for('adminArticleIndex'))

@app.route('/admin/article/delete/<id>')
def adminArticleDelete(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    Articles.objects(id=id).delete()
    flash('Berhasil dihapus!')
    return redirect(url_for('adminArticleIndex')) 

@app.route('/admin/article/edit/<id>')
def adminArticleEdit(id):
    if session.get('username') == None:
        return redirect(url_for('login'))
    categories = dbs.category.find()
    data = Articles.objects(id=id).first()
    
    form = ArticleForm(obj = data)
    return render_template('/CMS/article/edit.html', form=form, id=id, categories=categories)

@app.route('/admin/article/update/<title>', methods=['POST'])
def adminArticleUpdate(title):
    if session.get('username') == None:
        return redirect(url_for('login'))
    if request.files['banner']:
        file = request.files['banner']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(path)

        myquery = { "title": title }
        article_input = { "$set": { 
                        'title': request.form.get('title'), 
                        'category': request.form.get('category'), 
                        'tag': request.form.get('tag'),
                        'banner': request.files['banner'].filename,
                        'description': request.form.get('description'),
                        'writer': session["username"],
                        'published_date': request.form.get('published_date'),
                        'status': request.form.get('status')
                    } 
                }
        article_record.update_one(myquery, article_input)
    else:
        myquery = { "title": title }
        article_input = { "$set": { 
                        'title': request.form.get('title'), 
                        'category': request.form.get('category'), 
                        'tag': request.form.get('tag'),
                        'description': request.form.get('description'),
                        'writer': session["username"],
                        'published_date': request.form.get('published_date'),
                        'status': request.form.get('status')
                    } 
                }
        article_record.update_one(myquery, article_input)
                       
    flash('Berhasil diupdate!')
    return redirect(url_for('adminArticleIndex')) 
# END OF ADMIN ARTICLE

if __name__ == '__main__':
    app.run()