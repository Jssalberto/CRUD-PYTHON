from flask import Flask,render_template,url_for,request,redirect
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask import send_from_directory
from connect.connect import connect
from datetime import datetime
import os
app = Flask(__name__)

cursor = connect.cursor()
CARPETA = os.path.join("static/img")
app.config['CARPETA'] = CARPETA

@app.route("/img/<nuevo_nombre_images>")
def img(nuevo_nombre_images):
    return send_from_directory(app.config['CARPETA'],nuevo_nombre_images)
#! GET
#& SOLICITA UN RECURSO DEL SERVIDOR
@app.route("/")
def index():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template("index.html", users = users)

#! POST
#& ENVIA DATOS O RECURSOS AL SERVIDOR
@app.route("/enviar_datos/",methods=["GET","POST"])#/<id:int>
def enviar_datos():
    if request.method == "GET":
        return render_template("form.html")
    elif request.method == "POST":
        id = request.args.get("id")
        nombre = request.form["nombre"]
        usuario = request.form["usuario"]
        password = request.form["password"]
        image = request.files["image"]
        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        if image.filename != "":
            nuevo_nombre_images = tiempo+image.filename
            image.save("static/img/"+nuevo_nombre_images)
        sql = "INSERT INTO users VALUES(%s, %s, %s, %s,%s)"
        valores_users = (id, nombre,usuario,generate_password_hash(password),nuevo_nombre_images)
        cursor.execute(sql, valores_users)
        connect.commit()
        return redirect(url_for("index"))
    else:                       
        return render_template("form.html")
#! PUT
#& ACTUALIZA UN RECURSO EN EL SERVIDOR
#*CARGAR DATOS USUARIOS ACTUALIZAR
@app.route("/cargar_datos_users/<int:id>/")
def cargar_datos_users(id):
    cursor.execute("SELECT * FROM users WHERE id=%s",(id,))
    datos_users = cursor.fetchall()
    connect.commit()
    return render_template("update.html", datos_users=datos_users)           

@app.route("/update_users")
def update_users(): 
    id = request.form["txtID"]
    nombre = request.form["nombre"]
    usuario = request.form["usuario"]
    password = request.form["password"]
    image = request.files["image"]
    consulta_actualizar = "UPDATE users SET nombre=%s, usuario=%s, password=%s WHERE id=%s"
    datos_actualizar = (nombre, usuario, password, id)
    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")
    if image.filename != "":
        nuevo_nombre_images = tiempo+image.filename
        image.save("static/img/"+nuevo_nombre_images)
        cursor.execute("SELECT image FROM users WHERE id=%s", (id,))
        fila = cursor.fetchall()
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0]))
        cursor.execute("UPDATE users SET image=%s WHERE id=%s", (nuevo_nombre_images,id))
        connect.commit()
    cursor.execute(consulta_actualizar,datos_actualizar)
    connect.commit()
    return redirect(url_for("index"))
#! DELETE
#& ELIMINA UN RECURSO DEL SERVIDOR
@app.route("/delete_users/<int:id>/",methods=["GET"])
def delete_users(id):
    cursor.execute("SELECT image FROM users WHERE id=%s",(id,))
    fila = cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    cursor.execute("DELETE FROM users WHERE id=%s",(id,))
    connect.commit() 
    return redirect(url_for("index"))

@app.route("/form", methods=["GET"])
def form():
    return render_template("form.html")