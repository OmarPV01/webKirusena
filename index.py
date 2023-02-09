from fileinput import filename
import sqlite3
from flask import Flask
from flask import render_template,request,redirect,url_for,session
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import date, datetime
from notifypy import Notify
import smtplib
import ssl
from email.message import EmailMessage
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
@app.route('/Homedoc')
def homedoc():
    return render_template('Doctor/Homedoc.html')
@app.route('/home')
def homepac():
    return render_template("Paciente/HomePac.html")
@app.route('/about')
def about():
    return render_template('Paciente/about.html')

@app.route('/Pacientes')
def Pacientes():
    sql = "SELECT * FROM usuario where USU_ROL = 'P';"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    usuario = cursor.fetchall()
    conn.commit()
    return render_template('Doctor/Pacientes.html', usuario=usuario)

@app.route('/speach-to-text')
def speach():
    return render_template('Paciente/speech.html')
@app.route('/translate')
def translate():
    return render_template('Doctor/translate.html')

@app.route('/Recuperar',methods=['GET', 'POST'])
def Recuperar():
    if request.method == 'POST':
        _Correo = str(request.form['txtCorreo'])
        _DNI = str(request.form['txtDNI'])
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuario WHERE usu_correo=%s", (_Correo,))
        user = cur.fetchone()
        print(user)
        cur.close()
        if len(user) > 0:
            print('holi')
            if _Correo == user[11]:
                session['conectado'] = True
                session['nombre'] = user[2]
                session['email'] = user[11]
                session['DNI'] = user[1]
                session['password'] = user[10]
                if _DNI == user[1]:
                    # Definir remitente y receptor de correo electrónico
                    email_sender = 'salazarascenciop@gmail.com'
                    email_password = 'bklcaobnjwcjzaje'
                    email_receiver = _Correo

                    # CUERPO Y ASUNTO DEL CORREO
                    subject = 'RECUPERAR CONTRASEÑA'
                    body = session['nombre'] + """
                      SU CONTRASEÑA ES:  """ + session['password']

                    em = EmailMessage()
                    em['From'] = email_sender
                    em['To'] = email_receiver
                    em['Subject'] = subject
                    em.set_content(body)

                    # Agregar capa de Seguridad
                    context = ssl.create_default_context()

                    # Iniciar sesión y enviar el correo electrónico
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.login(email_sender, email_password)
                        smtp.sendmail(email_sender, email_receiver, em.as_string())
                        return render_template("login.html")

    return render_template('RecuperarCuenta.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        _Correo = request.form['txtCorreo']
        _Password = request.form['txtPassword']
        if _Correo =="" and _Password =="":
            return render_template("login.html", _Mensaje="Completar campos")
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuario WHERE USU_CORREO=%s",_Correo)
        user = cur.fetchone()
        print(user)
        print(user[2])
        cur.close()
        if user ==None:
            return render_template("login.html",_Mensaje="Usuario Invalido")
        if len(user) > 0:
            if _Password == user[10]:
                session['conectado'] = True
                session['nombre'] = user[2]
                session['email'] = user[11]
                session['tipo'] = user[12]
                session['id'] = user[0]
                if session['tipo'] == 'P':
                    notification = Notify()
                    notification.title = "Saludos Estimado Paciente " + user[2]
                    notification.send()
                    return render_template("Paciente/HomePac.html")
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

    if (_nombre =="" or _Correo == "" or _Password == ""):
       return render_template("login.html", msgNombre = "Completar campos")

    sql = "INSERT INTO usuario (USU_NOMBRE , USU_APE_PAT , USU_PASSWORD, USU_CORREO, USU_ROL,USU_FOTO) VALUES (%s, %s, %s, %s, %s, %s)"
    datos = (_nombre, _apellidoPat, _Password, _Correo, 'P', '1')
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()

    # Definir remitente y receptor de correo electrónico
    email_sender = 'salazarascenciop@gmail.com'
    email_password = 'bklcaobnjwcjzaje'
    email_receiver = _Correo

    # CUERPO Y ASUNTO DEL CORREO
    subject = 'CONFIRMACIÓN DE CUENTA CREADA'
    body = "BIENVENIDO ESTIMADO PACIENTE A LA COMUNIDAD DE APPKIRU SE CONFIRMA SU CREACIÓN DE CUENTA :" + _nombre + " " + _apellidoPat + """
                          SU CONTRASEÑA ES:  """ + _Password
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Agregar capa de Seguridad
    context = ssl.create_default_context()

    # Iniciar sesión y enviar el correo electrónico
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    return redirect('/')


@app.route('/Fotos/<nombreFoto>')
def Fotos(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route('/PerfilUsuario')
def PerfilUsuario():
    name = session['nombre']
    id = session['id']
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuario where USU_ID=%s", (id,))
    usuario = cur.fetchall()
    conn.commit()
    return render_template('Paciente/PerfilUsuario.html', usuario=usuario, name=name, id=id)

@app.route('/faq')
def faq():
    return render_template('Paciente/faq.html')

@app.route('/EditarUsuario/<int:USU_ID>')
def EditarUsuario(USU_ID):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuario where USU_ID=%s", (USU_ID,))
    usuario = cur.fetchall()
    conn.commit()
    return render_template('Paciente/EditarUsuario.html', usuario=usuario)

@app.route('/update',methods=['POST'])
def update():
    name = session['nombre']
    id = session['id']
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
    _Foto = request.files['txtFoto']
    print(_nombre)
    sql ="update usuario set USU_DNI=%s ,USU_NOMBRE= %s, USU_APE_PAT=%s, USU_APE_MAT=%s ,USU_DIREC=%s," \
         " USU_DISTRITO=%s,USU_FEC_NAC=%s,USU_SEXO=%s,USU_NUM_CEL=%s,USU_PASSWORD=%s," \
         " USU_CORREO=%s where USU_ID =%s"
    datos=(_DNI,_nombre,_apellidoPat,_apellidoMat,_direccion,_distrito,_FechaNac,_Sexo,_cel,_Password,
           _Correo,id)
    print(_nombre)
    conn = mysql.connect()
    cur=conn.cursor()
    now= datetime.now()
    tiempo=now.strftime("%Y%H%S")
    print(_nombre)
    if _Foto.filename!= '':
        nuevoNombreFoto=tiempo+_Foto.filename
        _Foto.save("Fotos/"+nuevoNombreFoto)

        cur.execute("SELECT USU_FOTO from usuario where USU_ID =%s", (id,))
        cur.execute("UPDATE usuario set USU_FOTO=%s where USU_ID =%s", (nuevoNombreFoto, id,))
        conn.commit()
    cur.execute(sql,datos)
    conn.commit()
    return redirect('/PerfilUsuario')


if __name__ == '__main__':
    app.run(debug=True)

