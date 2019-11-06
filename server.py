import os
import peeweedbevolve
from flask import Flask, render_template, request,flash,redirect,url_for
from models import Store,Warehouse,db,Product
from peewee import fn, JOIN

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')

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

@app.route("/store/new",methods=["GET"])
def store_new():
    return render_template('store.html')

@app.route("/store/create",methods=["POST"])
def store_create():
    s = Store(name=request.form['name'])
    if s.save():
        flash("Successfully saved")
        return redirect(url_for('stores_list'))
    else:
        flash(f"{s.errors}")
        return render_template('store.html',name=request.form['name'], errors=s.errors)

@app.route("/stores",methods=["GET"])
def stores_list():
    # join left outer to get those stores that have no warehouse at all
    data = Store.select(Store.name,Store.id,fn.Count(Warehouse.id).alias('num')).join(Warehouse, JOIN.LEFT_OUTER).group_by(Store.id).order_by(Store.id)
    return render_template('stores.html',data=data)    

@app.route("/store/<int:id>/delete",methods=["POST"])
def store_delete(id):
    s = Store.get_by_id(id)
    if s.delete_instance():
        flash("Successfully deleted")
    else:
        flash("Unable to delete")
    return redirect(url_for('stores_list'))

@app.route("/store/<int:id>",methods=["GET"])
def store_show(id):
    store = Store.get_by_id(id)
    # store = Store.select(Store.name,Store.id,fn.Count(Warehouse.id).alias('num')).join(Warehouse, JOIN.LEFT_OUTER).group_by(Store.id).where(Store.id==id)
    return render_template('store_show.html',store=store)

@app.route("/store/<int:id>/update",methods=["POST"])
def store_update(id):
    s = Store(id=id,name=request.form['name'])
    if s.save(only=[Store.name]):
        flash("Successfully updated")
    else:
        flash("Unable to update")
    return redirect(url_for('store_show',id=id))

@app.route("/warehouse/new",methods=["GET"])
def warehouse_new():
    stores = Store.select()
    return render_template('warehouse.html',stores=stores)

@app.route("/warehouse/create",methods=["POST"])
def warehouse_create():
    store = Store.get(id=request.form['store_id'])
    w = Warehouse(location=request.form['location'], store=store)
    if w.save():
        flash("Successfully saved")
        return redirect(url_for('warehouses_list'))
    else:
        return render_template('warehouse.html')

@app.route("/warehouses",methods=["GET"])
def warehouses_list():
    data = Warehouse.select()
    return render_template('warehouses.html',data=data)  

@app.route("/warehouse/<int:id>",methods=["GET"])
def warehouse_show(id):
    warehouse = Warehouse.get_by_id(id)
    stores = Store.select()
    return render_template('warehouse_show.html',warehouse=warehouse,stores=stores)

@app.route("/warehouse/update/<int:id>",methods=["POST"])
def warehouse_update(id):
    w = Warehouse(id=id,location=request.form['location'],store=request.form['store_id'])
    if w.save(only=[Warehouse.location,Warehouse.store]):
        flash("Successfully updated")
    else:
        flash("Unable to update")
    return redirect(url_for('warehouse_show',id=id))

@app.route("/warehouse/delete/<int:id>",methods=["POST"])
def warehouse_delete(id):
    w = Warehouse.get_by_id(id)
    if w.delete_instance():
        flash("Successfully deleted")
    else:
        flash("Unable to update")
    return redirect(url_for('warehouses_list'))
  
@app.route("/product/new",methods=["GET"])
def product_new():
    warehouses = Warehouse.select()
    return render_template('product.html',warehouses=warehouses)

@app.route("/product/create",methods=["POST"])
def product_create():
    p = Product(name=request.form['name'],description=request.form['desc'],color=request.form['color'], warehouse=request.form['warehouse_id'])
    if p.save():
        flash("Successfully saved")
    else:
        flash("Unable to create new product")
    return redirect(url_for('products_list'))

@app.route("/products",methods=["GET"])
def products_list():
    data = Product.select()
    return render_template('products.html',data=data)  

@app.route("/product/<int:id>",methods=["GET"])
def product_show(id):
    product = Product.get_by_id(id)
    warehouses = Warehouse.select()
    return render_template('product_show.html',product=product,warehouses=warehouses)

@app.route("/product/update/<int:id>",methods=["POST"])
def product_update(id):
    p = Product(id=id,name=request.form['name'],description=request.form['desc'],color=request.form['color'],warehouse=request.form['warehouse_id'])
    if p.save(only=[Product.name,Product.description,Product.color,Product.warehouse]):
        flash("Successfully updated")
    else:
        flash("Unable to update")
    return redirect(url_for('product_show',id=id))

@app.route("/product/delete/<int:id>",methods=["POST"])
def product_delete(id):
    p = Product.get_by_id(id)
    if p.delete_instance():
        flash("Successfully deleted")
    else:
        flash("Unable to delete")
    return redirect(url_for('products_list'))

if __name__ == '__main__' :
    app.run()