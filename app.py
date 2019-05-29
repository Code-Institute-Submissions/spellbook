import os
from flask import Flask, render_template, redirect, session, request, url_for
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

# If statement to ensure env vars and debug are set appropriately for deployment

if os.environ.get('C9_HOSTNAME'):
    import config
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MONGO_URI'] = config.MONGO_URI
    app.config['DB_NAME'] = config.DB_NAME
else:
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["DB_NAME"] = os.getenv("DB_NAME")
    
# Init Mongo app through Flask_PyMongo

mongo = PyMongo(app)

# Read 

@app.route('/')     
@app.route('/index')
def index ():
    return render_template("index.html")

@app.route('/browse_spells')
def browse_spells():
    return render_template("view_spells.html", spells=mongo.db.spells.find(),
    components=mongo.db.components.find())

# Create spells

@app.route('/add_spell')
def add_spell():
    return render_template("add_spell.html", components=mongo.db.components.find(), 
    spells=mongo.db.spells.find(), die=mongo.db.die.find(),
    level=mongo.db.level.find(), school=mongo.db.school.find())
    
@app.route('/insert_spell', methods=['POST'])
def insert_spell():
    spells = mongo.db.spells
    spells.insert_one({'spell_name':request.form.get('spell_name'),
        'spell_level':request.form.get('spell_level'),
        'school': request.form.get('school'),
        'casting_time': request.form.get('casting_time'),
        'range':request.form.get('range'),
        'components':request.form.getlist('components'),
        'duration':request.form.get('duration'),
        'die_value':request.form.get('die_value'),
        'die_amount':request.form.get('die_amount')})
    return redirect(url_for('browse_spells'))
    
# Delete

@app.route('/delete_spell/<spell_id>')
def delete_spell(spell_id):
    mongo.db.spells.remove({'_id': ObjectId(spell_id)})
    return redirect(url_for('browse_spells'))    
    
# Update

# 28/05 Passing the spell to be edited components array in as its own var
# that array needs to be compared to the components array with selected ones showing up

@app.route('/edit_spell/<spell_id>')
def edit_spell(spell_id):
    the_spell = mongo.db.spells.find_one({"_id": ObjectId(spell_id)})
    component = the_spell['components']
    print(component)
    return render_template('edit_spell.html', spell=the_spell, 
    components=mongo.db.components.find(), die=mongo.db.die.find(), level=mongo.db.level.find(),
    school=mongo.db.school.find(), component=component)

@app.route('/update_spell/<spell_id>', methods=["POST"])
def update_spell(spell_id):
    spells = mongo.db.spells
    spells.update( {'_id': ObjectId(spell_id)},
    {
        'spell_name':request.form.get('spell_name'),
        'spell_level':request.form.get('spell_level'),
        'school': request.form.get('school'),
        'casting_time': request.form.get('casting_time'),
        'range':request.form.get('range'),
        'components':request.form.getlist('components'),
        'duration':request.form.get('duration'),
        'die_value':request.form.get('die_value'),
        'die_amount':request.form.get('die_amount')
    })
    return redirect(url_for('browse_spells'))
    
    
# Search

# 23/05/19 search function landing on a "if no direction is specified, key_or_list must be an instance of list" message 
    
@app.route('/search_request', methods=['POST', 'GET'])
def search_request():
    spells=mongo.db.spells
    search_name=str(request.form.get('spell_name'))
    print(search_name)
    results = spells.find({"spell_name": "search_name"})
    return render_template('searched_spells.html', results=results, spells=spells)
    

# Login/Register 

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/register_request', methods=['POST', 'GET'])
def register_request():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username':request.form['user_name']})
        
        if existing_user is None:
            users.insert({'username':request.form['user_name']})
            session['user_name'] = request.form['user_name']
            return redirect(url_for('index'))
            
        return 'That username has already been choosen!'
    
    return render_template('register.html')        


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')))

#spells=mongo.db.spells
#    spells.create_index([{"$**":"text"}])
#    search_name=request.form.get('spell_name')
#    print(search_name)
#    results=spells.find({"$text":{"$search":search_name}})
#    print(results)
#    return render_template('searched_spells.html', results=results, spells=spells.find())