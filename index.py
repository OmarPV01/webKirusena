from fileinput import filename
import sqlite3
from flask import Flask
from flask import render_template,request,redirect,url_for,session
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import date, datetime
from notifypy import Notify
import os


app= Flask(__name__)
app.secret_key = "super secret key"
app.config['SESSION_TYPE'] = 'filesystem'


mysql= MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='appkiru'
mysql.init_app(app)

CARPETA=os.path.join('Fotos')
app.config['CARPETA'] = CARPETA



@app.route('/')
def home():
        return render_template('login.html')

@app.route('/')
def HomePaciente():
        return render_template('home.html')

@app.route('/Homedoc')
def Homedoc():
        return render_template('Homedoc.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/speach-to-text')
def speach():
    return render_template('speech.html')
@app.route('/translate')
def translate():
    return render_template('translate.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        _Correo = request.form['txtCorreo']
        _Password = request.form['txtPassword']
        print(_Password)
        print(_Correo)

        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuario WHERE USU_CORREO=%s",_Correo)
        user = cur.fetchone()
        print(user)
        print(user[2])
        cur.close()

        if len(user) > 0:
            print(_Password)
            print('holi2')
            print('holi')
            if _Password == user[10]:
                session['conectado'] = True
                session['nombre'] = user[2]
                session['email'] = user[11]
                session['tipo'] = user[12]

                if session['tipo'] == 'P':
                    notification = Notify()
                    notification.title = "Saludos Estimado Paciente " + user[2]
                    notification.send()
                    return render_template("Paciente/home.html")
                elif session['tipo'] == 'D':
                    notification = Notify()
                    notification.title = "Saludos Estimado Doctor " + user[2]
                    notification.send()
                    return render_template("Doctor/HomeDoc.html")


            else:
                notification = Notify()
                notification.title = "Error de Acceso"
                notification.message = "Correo o contraseña no valida"
                notification.send()
                return render_template("login.html")
        else:
            notification = Notify()
            notification.title = "Error de Acceso"
            notification.message = "No existe el usuario"
            notification.send()
            return render_template("login.html")
    else:

        return render_template("login.html")

@app.route('/create')
def create():
    return render_template('createUsuario.html')

@app.route('/creationUsuario', methods=['POST'])
def creationUsuario():
    _nombre = request.form['txtNombre']
    _apellidoPat = request.form['txtApellidoPat']
    _Password = request.form['txtPassword']
    _Correo = request.form['txtCorreo']
    _Rol = request.form['txtRol']

    sql = "INSERT INTO usuario (USU_ID ,USU_NOMBRE , USU_APE_PAT , USU_PASSWORD, USU_CORREO, USU_ROL) VALUES ( null,%s ,%s,%s ,%s, %s)"
    datos = (_nombre, _apellidoPat, _Password, _Correo,_Rol)
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/Fotos/<nombreFoto>')
def Fotos(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/Pacientes')
def Pacientes():
    sql = "SELECT * FROM usuario;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    usuario = cursor.fetchall()
    conn.commit()
    return render_template('Doctor/Pacientes.html', usuario=usuario)



@app.route('/EditarUsuario/<int:USU_ID>')
def EditarUsuario(USU_ID):
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM usuario where USU_ID=%s",(USU_ID))
    usuario=cursor.fetchall()
    conn.commit()
    return render_template('EditarUsuario.html', usuario=usuario)

@app.route('/update',methods=['POST'])
def update():
    _DNI = request.form['txtDNI']
    _nombre = request.form['txtNombre']
    _apellidoPat = request.form['txtApellidoPat']
    _apellidoMat = request.form['txtApellidoMat']
    _direccion = request.form['txtDire']
    _distrito = request.form['txtDistrito']
    _FechaNac = request.form['txtFech']
    _Sexo = request.form['txtSex']
    _cel = request.form['txtCel']
    _Password = request.form['txtPassword']
    _Correo = request.form['txtCorreo']
    _Rol = request.form['txtRol']
    _Foto = request.files['txtFoto']
    USU_ID=request.form['txtId']

    sql ="update usuario set USU_DNI=%s ,USU_NOMBRE= %s, USU_APE_PAT=%s, USU_APE_MAT=%s ,USU_DIREC=%s," \
         " USU_DISTRITO=%s,USU_FEC_NAC=%s,USU_SEXO=%s,USU_NUM_CEL=%s,USU_PASSWORD=%s," \
         " USU_CORREO=%s,USU_ROL=%s where USU_ID =%s"

    datos=(_DNI,_nombre,_apellidoPat,_apellidoMat,_direccion,_distrito,_FechaNac,_Sexo,_cel,_Password,
           _Correo,_Rol,USU_ID)
    conn = mysql.connect()
    cursor=conn.cursor()

    now= datetime.now()
    tiempo=now.strftime("%Y%H%S")

    if _Foto.filename!= '':
        nuevoNombreFoto=tiempo+_Foto.filename
        _Foto.save("Fotos/"+nuevoNombreFoto)

        cursor.execute("SELECT USU_FOTO from usuario where USU_ID =%s",USU_ID)
        cursor.execute("UPDATE usuario set USU_FOTO=%s where USU_ID =%s",(nuevoNombreFoto,USU_ID))
        conn.commit()
    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

