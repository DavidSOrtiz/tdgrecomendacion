from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc

# initializations
app = Flask(__name__)

# settings
app.secret_key = "mysecretkey"

cadenaConexion = """Driver={ODBC Driver 17 for SQL Server};
              Server=tcp:tdg2020.database.windows.net,1433;
              Database=dbRecomendacion;
              Uid=sebas;
              Pwd=Tdg2020@.Itm;
              Encrypt=yes;
              TrustServerCertificate=no;
              Connection Timeout=30;"""

# routes
@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/Registrate')
def Registro():
    conn = pyodbc.connect(cadenaConexion)
    cur = conn.cursor()
    cur.execute('SELECT * FROM tema')
    temas = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return render_template('Registrate.html', temas = temas)

@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        Names = request.form['Names']
        Email = request.form['Email']
        password = request.form['password']
        idtema = request.form['idtema']
        conn = pyodbc.connect(cadenaConexion)
        cur = conn.cursor()
        cur.execute('INSERT INTO usuario (nombre, correo, clave, id_tema) VALUES(?,?,?,?)', (Names, Email, password, idtema))
        conn.commit()
        cur.close()
        conn.close()
        flash('Estudiante ingresado correctamente.')
        return redirect(url_for('index'))

@app.route('/Accessing', methods=['POST', "GET"])
def Accessing():
    if request.method == 'POST' or request.method == 'GET':
        conn = pyodbc.connect(cadenaConexion)
        cur = conn.cursor()
        if request.method == 'POST':
            Usuario = request.form['Usuario']
            Contrasena = request.form['Contrasena']
            cur.execute('SELECT * FROM usuario WHERE correo = ? And clave = ?' , (Usuario, Contrasena))
            Usuario = cur.fetchall()
            if len(Usuario) > 0:
                for row in Usuario:
                    session['idUser'] = row[0]
                    idUser = row[0]
                    session['NomUser'] = row[1]
        else:
            if 'idUser' in session and 'NomUser' in session:
                idUser = session['idUser']
                cur.execute('SELECT * FROM usuario WHERE id_user = ?' , (idUser))
                Usuario = cur.fetchall()
            else:
                return render_template('index.html')
        if len(Usuario) > 0:  
            cur.execute('SELECT * FROM test_felder WHERE id_user = ?' , (idUser))
            data = cur.fetchall()
            return render_template('menu.html', Usuario = Usuario[0], Datos = data)
        else:
            flash('La información ingresada no es correcta.')
            return render_template('index.html')
        cur.close()
        conn.close()
    
@app.route('/recomendaciones', methods=['POST','GET'])
def recomendaciones():
    session['id_objeto'] = ""
    if 'idUser' in session and 'NomUser' in session:
        if 'idUser' in session:
            id = session['idUser']
            conn = pyodbc.connect(cadenaConexion)
            cur = conn.cursor()
            cur.execute('SELECT * FROM test_result WHERE id_user = ?' , (id))
            resultados = cur.fetchall()
            if len(resultados) > 0:
                cur.execute('SELECT * FROM [dbo].[valoracion] Where id_user = ?' , (id))
                calificaciones = cur.fetchall()
                if len(calificaciones) <= 5:
                    lista = ""
                    cur.execute('SELECT id_contexto FROM [dbo].[gusto] Where id_user = ?' , (id))
                    gustos = cur.fetchall()
                    for gusto in gustos:
                        lista = lista + str(gusto[0]) + ","
                    lista = lista[0:len(lista)-1]
                    for resultado in resultados:
                        perfil = resultado[2]
                        if perfil == "Reflexivo":
                            act_ref = "Reflexivo"
                        elif perfil == "Activo":
                            act_ref = "Activo"
                        elif perfil == "Intuitivo":
                            sen_int = "Intuitivo"
                        elif perfil == "Sensorial":
                            sen_int = "Sensorial"
                        elif perfil == "Visual":
                            vis_ver = "Visual"
                        elif perfil == "Verbal":
                            vis_ver = "Verbal"
                        elif perfil == "Global":
                            sec_glo = "Global"
                        elif perfil == "Secuencial":
                            sec_glo = "Secuencial"
                    sql = """SELECT * FROM [dbo].[objeto] WHERE act_ref = '""" + act_ref + """' and sen_int = '""" + sen_int + """' and vis_ver = '""" + vis_ver + """' and sec_glo = '""" + sec_glo + """' And id_tema = """ + str(id) + """ and id_contexto in(""" + lista + """)
                                    Union all
                                    SELECT * FROM [dbo].[objeto] WHERE act_ref = '""" + act_ref + """' and sen_int = '""" + sen_int + """' and vis_ver = '""" + vis_ver + """' and sec_glo = '""" + sec_glo + """' And id_tema = """ + str(id) + """
                                    Union all
                                    SELECT * FROM [dbo].[objeto] WHERE act_ref = '""" + act_ref + """' and vis_ver = '""" + vis_ver + """' and sec_glo = '""" + sec_glo + """' And id_tema = """ + str(id) + """
                                    Union all
                                    SELECT * FROM [dbo].[objeto] WHERE vis_ver = '""" + vis_ver + """' and sec_glo = '""" + sec_glo + """' And id_tema = """ + str(id) + """
                                    Union all
                                    SELECT * FROM [dbo].[objeto] WHERE vis_ver = '""" + vis_ver + """' And id_tema = """ + str(id) + """
                                    Union all
                                    SELECT * FROM [dbo].[objeto] WHERE id_tema = """ + str(id)
                    cur.execute(sql)
                    recomendaciones = cur.fetchall()
                    for recomendacion in recomendaciones:
                        id_objeto = recomendacion[0]
                        cur.execute('SELECT * FROM [dbo].[valoracion] Where id_user = ? and id_objeto = ?' , (id, id_objeto))
                        data = cur.fetchall()
                        if len(data) == 0:
                            break
                        else:
                            id_objeto = ""
                    if id_objeto != "":
                        cur.execute('SELECT [descripcion],[entrada],[salida],[ejmEntrada],[ejmSalida] FROM [objeto] WHERE [id_objeto] = ?' , (id_objeto))
                        data = cur.fetchall()
                        session['id_objeto'] = id_objeto
                        return render_template('recomendaciones.html', data = data[0])
                    else:
                        return render_template('recomendaciones.html', data = "Sin recomendaciones")
                    return render_template('recomendaciones.html', data = data[0])
                else:
                    cur.execute('SELECT [id_user],[id_objeto],[valoracion] FROM [dbo].[recomendacion] Where id_user = ? Order by valoracion Desc' , (id))
                    recomendaciones = cur.fetchall()
                    for recomendacion in recomendaciones:
                        id_objeto = recomendacion[1]
                        cur.execute('SELECT * FROM [dbo].[valoracion] Where id_user = ? and id_objeto = ?' , (id, id_objeto))
                        data = cur.fetchall()
                        if len(data) == 0:
                            break
                        else:
                            id_objeto = ""
                    if id_objeto != "":
                        cur.execute('SELECT [descripcion],[entrada],[salida],[ejmEntrada],[ejmSalida] FROM [objeto] WHERE [id_objeto] = ?' , (id_objeto))
                        data = cur.fetchall()
                        session['id_objeto'] = id_objeto
                        return render_template('recomendaciones.html', data = data[0])
                    else:
                        return render_template('recomendaciones.html', data = "Sin recomendaciones")
            else:
                return render_template('formulario.html', estudianteid = id)
            cur.close()
            conn.close()
    else:
        return render_template('index.html')

@app.route('/EliminarContexto/<id>', methods=['GET'])
def EliminarContexto(id):
    conn = pyodbc.connect(cadenaConexion)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM gusto
        WHERE id_gusto = ?
    """, (id))
    conn.commit()
    cur.close()
    conn.close()
    flash('Contexto eliminado correctamente.')
    return redirect(url_for('contextos'))

@app.route('/calificacion', methods=['POST'])
def calificacion():
    if 'id_objeto' in session:
        return render_template('calificacion.html')
    else:
        return render_template('index.html')

@app.route('/guardarcalificacion', methods=['POST'])
def save_calificacion():
    if 'id_objeto' in session:
        if request.method == 'POST':
            id = session['idUser']
            id_objeto = session['id_objeto']
            calificacion = request.form['star']
            conn = pyodbc.connect(cadenaConexion)
            cur = conn.cursor()
            cur.execute('INSERT INTO valoracion (id_user, id_objeto, valoracion) VALUES(?,?,?)', (id, id_objeto, calificacion))
            conn.commit()
            return redirect(url_for('recomendaciones'))
    else:
        return render_template('index.html')

@app.route('/add_contexto', methods=['POST'])
def add_contexto():
    if 'idUser' in session and 'NomUser' in session:
        if request.method == 'POST':
            id = session['idUser']
            id_contexto = request.form['idfaltante']
            conn = pyodbc.connect(cadenaConexion)
            cur = conn.cursor()
            cur.execute('INSERT INTO gusto (id_contexto, id_user) VALUES(?,?)', (id_contexto, id))
            conn.commit()
            flash('Contexto agregado correctamente.')
            return redirect(url_for('contextos'))
    else:
        return render_template('index.html')

@app.route('/editar_estudiante')
def editar_estudiante():
    if 'idUser' in session and 'NomUser' in session:
        id = session['idUser']
        conn = pyodbc.connect(cadenaConexion)
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuario WHERE id_user = ?' , (id))
        data = cur.fetchall()
        cur.execute('SELECT * FROM tema')
        temas = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('editar_estudiante.html', estudiante = data[0], temas = temas)
    else:
        return render_template('index.html')

@app.route('/contextos')
def contextos():
    if 'idUser' in session and 'NomUser' in session:
        id = session['idUser']
        conn = pyodbc.connect(cadenaConexion)
        cur = conn.cursor()
        cur.execute('SELECT id_gusto, contexto FROM gusto inner join contexto on gusto.id_contexto = contexto.id_contexto WHERE id_user = ?' , (id))
        gustos = cur.fetchall()
        if len(gustos) > 0:
            Mensaje = "Con Datos"
        else:
            Mensaje = "Sin Datos"
        cur.execute('SELECT id_contexto, contexto FROM contexto WHERE id_contexto NOT IN (SELECT id_contexto FROM gusto where id_user = ?) Order By contexto Asc', (id))
        faltates = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('contextos.html', gustos = gustos, faltates = faltates, Mensaje = Mensaje)
    else:
        return render_template('index.html')

@app.route('/update', methods=['POST'])
def edit_estudiante():
    if 'idUser' in session and 'NomUser' in session:
        if request.method == 'POST':
            id = session['idUser']
            Names = request.form['Names']
            Email = request.form['Email']
            Password = request.form['Password']
            idtema = request.form['idtema']
            conn = pyodbc.connect(cadenaConexion)
            cur = conn.cursor()
            cur.execute("""
                UPDATE usuario
                SET nombre = ?,
                correo = ?,
                clave = ?,
                id_tema = ?
                WHERE id_user = ?
            """, (Names, Email, Password, idtema, id))
            conn.commit()
            cur.close()
            conn.close()
            flash('Estudiante actualizado correctamente.')
            return redirect(url_for('Accessing'))
    else:
        return render_template('index.html')

@app.route('/responder_formulario', methods=['GET'])
def responder_formulario():
    if 'idUser' in session and 'NomUser' in session:
        if request.method == 'GET':
            if 'idUser' in session:
                id = session['idUser']
                conn = pyodbc.connect(cadenaConexion)
                cur = conn.cursor()
                cur.execute('SELECT * FROM test_felder WHERE id_user = ?' , (id))
                data = cur.fetchall()
                cur.execute('SELECT * FROM test_result WHERE id_user = ?' , (id))
                data1 = cur.fetchall()
                cur.close()
                conn.close()
                if len(data) > 0:
                    return render_template('formularioResuelto.html', preguntas = data, perfiles = data1)
                else:
                    return render_template('formulario.html', estudianteid = id)
    else:
        return render_template('index.html')

@app.route('/GrabarFormulario', methods=['POST'])
def Grabar_Formulario():
    if 'idUser' in session and 'NomUser' in session:
        if request.method == 'POST':
            id = session['idUser']
            Act_RefA = 0
            Act_RefB = 0
            Sens_IntA = 0
            Sens_IntB = 0
            Vis_VerbA = 0
            Vis_VerbB = 0
            Sec_GlobA = 0
            Sec_GlobB = 0
            for Contador in range(44):
                Dato = request.form['' + str(Contador + 1) + '']
                Pregunta = Contador + 1
                Respuesta = Dato[-1:]
                conn = pyodbc.connect(cadenaConexion)
                cur = conn.cursor()
                cur.execute('INSERT INTO test_felder (id_user, id_question, respuesta) VALUES(?,?,?)', (id, Pregunta, Respuesta))
                conn.commit()
                if Pregunta % 4 == 1:
                    if Respuesta == "A":
                        Act_RefA = Act_RefA + 1
                    else:
                        Act_RefB = Act_RefB + 1
                elif Pregunta % 4 == 2:
                    if Respuesta == "A":
                        Sens_IntA = Sens_IntA + 1
                    else:
                        Sens_IntB = Sens_IntB + 1
                elif Pregunta % 4 == 3:
                    if Respuesta == "A":
                        Vis_VerbA = Vis_VerbA + 1
                    else:
                        Vis_VerbB = Vis_VerbB + 1
                elif Pregunta % 4 == 0:
                    if Respuesta == "A":
                        Sec_GlobA = Sec_GlobA + 1
                    else:
                        Sec_GlobB = Sec_GlobB + 1
            if Act_RefA > Act_RefB:
                Preferencia = "Activo"
                Calculo = Act_RefA - Act_RefB
            else:
                Preferencia = "Reflexivo"
                Calculo = Act_RefB - Act_RefA
            cur.execute('INSERT INTO test_result (id_user, perfil, puntaje) VALUES(?,?,?)', (id, Preferencia, Calculo))
            conn.commit()
            if Sens_IntA > Sens_IntB:
                Preferencia = "Sensorial"
                Calculo = Sens_IntA - Sens_IntB
            else:
                Preferencia = "Intuitivo"
                Calculo = Sens_IntB - Sens_IntA
            cur.execute('INSERT INTO test_result (id_user, perfil, puntaje) VALUES(?,?,?)', (id, Preferencia, Calculo))
            conn.commit()
            if Vis_VerbA > Vis_VerbB:
                Preferencia = "Visual"
                Calculo = Vis_VerbA - Vis_VerbB
            else:
                Preferencia = "Verbal"
                Calculo = Vis_VerbB - Vis_VerbA
            cur.execute('INSERT INTO test_result (id_user, perfil, puntaje) VALUES(?,?,?)', (id, Preferencia, Calculo))
            conn.commit()
            if Sec_GlobA > Sec_GlobB:
                Preferencia = "Secuencial"
                Calculo = Sec_GlobA - Sec_GlobB
            else:
                Preferencia = "Global"
                Calculo = Sec_GlobB - Sec_GlobA
            cur.execute('INSERT INTO test_result (id_user, perfil, puntaje) VALUES(?,?,?)', (id, Preferencia, Calculo))
            conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('Accessing'))
    else:
        return render_template('index.html')

# starting the app
if __name__ == "__main__":
    app.run(port=3000, debug=True)
