import peeweedbevolve
from flask import Flask, render_template, request,flash,redirect,url_for
from models import Store,Warehouse,db
from peewee import fn, JOIN

app = Flask(__name__)
app.secret_key = b'\xa8\x1a:\xc4*\xf4\x1b&\xf8\x840\x1c\xe0TYT'

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response

@app.cli.command()
def migrate():
    db.evolve(ignore_tables={'base_model'})

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/store")
def store():
    return render_template('store.html')

@app.route("/create",methods=["POST"])
def create():
    s = Store(name=request.form['name'])
    if s.save():
        flash("Successfully saved")
        return redirect(url_for('store'))
    else:
        return render_template('store.html',name=request.form['name'])

@app.route("/stores")
def stores_list():
    data = Store.select(Store.name,Store.id,fn.Count(Warehouse.id).alias('num')).join(Warehouse, JOIN.LEFT_OUTER).group_by(Store.id).order_by(Store.id)
    return render_template('stores.html',data=data)    

@app.route("/delete_store/<int:id>",methods=["POST"])
def delete_store(id):
    s = Store.get_by_id(id)
    if s.delete_instance():
        flash("Successfully deleted")
        return redirect(url_for('stores_list'))
    else:
        return render_template('stores.html',id=id)    

@app.route("/store/<int:id>")
def show(id):
    store = Store.select(Store.name,Store.id,fn.Count(Warehouse.id).alias('num')).join(Warehouse, JOIN.LEFT_OUTER).group_by(Store.id).where(Store.id==id)
    return render_template('store_page.html',store=store)

@app.route("/edit_store/<int:id>",methods=["POST"])
def edit_store(id):
    s = Store(id=id,name=request.form['name'])
    if s.save(only=[Store.name]):
        flash("Successfully updated")
        return redirect(url_for('show',id=id))
    else:
        return render_template('store_page.html',name=request.form['name'])

@app.route("/warehouse")
def warehouse():
    stores = Store.select()
    return render_template('warehouse.html',stores=stores)

@app.route("/create_warehouse",methods=["POST"])
def create_warehouse():
    store = Store.get(name=request.form['store_id'])
    w = Warehouse(location=request.form['location'], store=store)
    if w.save():
        flash("Successfully saved")
        return redirect(url_for('warehouse'))
    else:
        return render_template('warehouse.html',name=request.form['location'])

if __name__ == '__main__' :
    app.run()