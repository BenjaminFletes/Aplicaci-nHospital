from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk    
from tkinter import Menu, Toplevel, messagebox, Frame
from tkinter import ttk
import psycopg2
from datetime import date
from tkcalendar import Calendar
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import re


background = "#03283D"
framebg = "#EDEDED"
framefg = "#06283D"
global noIntentos, nombre_usuario, user, password, root, elementos, usuario_actual, dia_elegido
dia_elegido = None
user_admin = "admin"
pass_admin = "1234"
noIntentos = 0
elementos_actuales = []
datosEmpleado = ["Código", "Nombre", "Dirección", "Teléfono", "Nacimiento", "Sexo", "Sueldo", "Turno", "Contraseña"]
datosDoctor = ["Código", "Nombre", "Dirección", "Teléfono", "Nacimiento", "Sexo", "Especialidad", "Contraseña"]
datosPaciente = ["Código", "Nombre", "Dirección", "Teléfono", "Nacimiento", "Sexo", "Edad", "Estatura"]
datosMedicamento = ["Código","Nombre","Administración", "Presentación", "Caducidad"]
listaPacientes = {}
listaDoctores = {}
listaEmpleados = {}
listaCitas = []
listaConsultas = []
listaMedicamento = {}

def conectar_base():
    try:
        conexion = psycopg2.connect(
            host = "localhost",
            database = "Proyecto",
            user = "postgres",
            password = "lolsito197",
            port = "5432"
        )
        return conexion

    except psycopg2.Error as e:
        print(f'Error al conectar a PostgreSQL {e}')
        return None
    #--------------------------------------------------------------------------------------------
def pasar(event):
    event.widget.config(bg="lightblue")

def sacar(event):
    event.widget.config(bg="#C8D9D3")

def sacar2(event):
    event.widget.config(bg="#D9D9D9")

def crear_entry(master, nombre, x, y, w, h, **kwargs):
    entry = tk.Entry(master, width=w, fg="#000", border=0, bg="#D9D9D9", font=('helvetica', 14), **kwargs)
    entry.name = nombre
    entry.insert(0, nombre)
    entry.place(x=x, y=y)
    return entry

def crear_texto(master, nombre, x, y, w, h, s):
    label = tk.Label(master, text = nombre,bg="#fff", anchor="e",font=('helvetica', s, 'bold'))
    label.name = nombre
    label.place(x=x, y=y, width=w, height=h)
    elementos_actuales.extend([label])
    return label

def crear_label(master, nombre, x, y, w, h):
    if nombre == "Pacientes" or nombre == "Empleados" or nombre == "Citas"or  nombre == "Doctores" or nombre=="Medicamento":
        label = tk.Label(master, text = nombre, width = 21, fg="#262626",font=("helvetica", 18, "bold"),bg="#C8D9D3")
        label.bind("<Leave>", sacar)
    else:
        label = tk.Label(master, text = nombre, width=21, bg="#D9D9D9", font=('helvetica', 22, 'bold'))
        label.bind("<Leave>", sacar2)
    label.name = nombre
    label.place(x=x, y=y, width=w, height=h)
    label.bind("<Enter>", pasar)

    return label

    #--------------------------------------------------------------------------------------------
def crear_pdf(a, diagnostico, medicamento):
    nombre_pdf = "consulta_" + re.sub(r'\W+', '_', a[1]) + "_" + a[3]
    pdf_file = nombre_pdf+".pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    c.setTitle("Consulta Médica")
    c.setFont("Helvetica-Bold", 16)

    # Títulop
    c.drawCentredString(300, 770, "CONSULTA MÉDICA")

    #linea negre
    c.setLineWidth(1)
    try:
        c.drawImage("imagenes/icono.png", 15, 755, width=35, height=35)  
    except Exception as e:
        print(f"No se pudo cargar la imagen: {e}")
    c.line(50, 760, 550, 760)

    # Info
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, "Fecha de consulta:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 730, a[3])  # Fecha

    c.setFont("Helvetica", 12)
    c.drawString(50, 710, "Hora de consulta:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 710, a[4])  # Hora

    c.setFont("Helvetica", 12)
    c.drawString(50, 690, "Nombre del doctor:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 690, nombre_usuario[1])  # Nombre del doctore

    c.setFont("Helvetica", 12)
    c.drawString(50, 670, "Paciente:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 670, a[1])  # Nombre del paciente

    c.setFont("Helvetica", 12)
    c.drawString(50, 620, "Diagnóstico:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(150, 620, diagnostico)  # Diagnóstico

    c.setFont("Helvetica", 12)
    c.drawString(50, 440, "Medicamento recetado:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 440, medicamento)  # Medicamento

    # Línea
    c.setStrokeColor(colors.lightgrey)
    c.setLineWidth(0.5)
    c.line(50, 420, 550, 420)

    # Nota abajo que dice que es generada
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    c.drawString(50, 400, "Consulta generada automáticamente por el sistema.")

    # Guardar el PDF
    c.save()


def actualizar_listas():
    conectar = conectar_base()
    if conectar:
        listaCitas.clear()
        cursor = conectar.cursor()
        try:
            cursor.execute("SELECT codigo, nombre FROM paciente;")
            for i in cursor.fetchall():
                listaPacientes[i[0]] = i[1]
            cursor.execute("SELECT codigo, nombre FROM doctor;")
            for i in cursor.fetchall():
                listaDoctores[i[0]] = i[1]
            cursor.execute("SELECT codigo, nombre FROM empleado;")
            for i in cursor.fetchall():
                listaEmpleados[i[0]] = i[1]
            cursor.execute("SELECT * FROM cita ORDER BY codigo;")
            for i in cursor.fetchall():
                listaCitas.extend([i[0]])
            cursor.execute("SELECT codigo, nombre FROM medicamento;")
            for i in cursor.fetchall():
                listaMedicamento[i[0]] = i[1]
            cursor.execute("SELECT codigo FROM consulta;")
            for i in cursor.fetchall():
                listaConsultas.extend([i[0]])
        except Exception as e:
            messagebox.showerror("Error", f"Error al conectar: {e}")
        finally:
            cursor.close()
            conectar.close()

def mostrar_opciones(master, target, posx, posy,label):
    def seleccionar(event):
        seleccion = listbox.curselection()
        if seleccion:
            item = listbox.get(seleccion)
            label.configure(text=item, font = ("helvetica", 10, "bold"))
        listbox.destroy()

    listbox = tk.Listbox(master,height=0, width=55, bg="#E5E1D7")
    actualizar_listas()
    for item in elementos_actuales:
        if isinstance(item, tk.Listbox):
            item.destroy()
    if target == "paciente":
        for clave, valor in listaPacientes.items():
            listbox.insert(tk.END, valor)
    elif target == "doctor":
        for clave, valor in listaDoctores.items():
            listbox.insert(tk.END, valor)
    elif target == "empleado":
        for clave, valor in listaEmpleados.items():
            listbox.insert(tk.END, valor)
    elif target == "cita":
        print(listaCitas)
        for valor in listaCitas:
            listbox.insert(tk.END, valor)
    elif target == "medicamento":
        for clave, valor in listaMedicamento.items():
            listbox.insert(tk.END, valor)
    listbox.bind("<<ListboxSelect>>", seleccionar)
    listbox.place(x = posx, y = posy+10)
    elementos_actuales.extend([listbox])


def cerrar_sesion(x):
    confirmar = messagebox.askyesno("Cerrar sesión", "¿Estás seguro de que quieres cerrar sesión?")
    if confirmar:
        limpiar_pantalla()
        x.destroy()  # Cerrar la ventana principal
        iniciar_sesion()

def limpiar_pantalla():
    """Elimina todos los widgets en la lista 'elementos_actuales' de la interfaz."""
    for widget in elementos_actuales:
        widget.destroy()
    elementos_actuales.clear()  # Limpia la lista después de eliminar los widgets
    actualizar_listas()
    global dia_elegido
    dia_elegido = None

def sesion_iniciada(usuario):
    global dia_elegido
    global nombre_usuario

    def crear_menu(target):
        limpiar_pantalla()
        #cambiar-------------------------------------
        if target == "cita":
            if usuario_actual == "admin" or usuario_actual=="empleado":
                registrar = crear_label(x, 'Registrar %s' % target, 300,190, 350, 50)
                registrar.bind("<Button-1>", lambda event: registrar_cita(x, "registrar","x"))
                eliminar = crear_label(x, 'Eliminar %s' % target, 300,260, 350, 50)
                eliminar.bind("<Button-1>", lambda event: eliminar_cita())
                modificar = crear_label(x, 'Modificar %s' % target, 300,330, 350, 50)
                modificar.bind("<Button-1>", lambda event: elegir(target))
                ver = crear_label(x, 'Ver citas', 300,400, 350, 50)
                ver.bind("<Button-1>", lambda event: visualizar_cita('todo',0,0,"b"))
                elementos_actuales.extend([registrar, eliminar, modificar, ver])

            elif usuario_actual == "doctor":
                etiqueta = crear_texto(frame, 'Ver citas por...', 240,100, 350, 50,20)
                dia = crear_label(x, 'Dia', 300,190, 350, 50)
                dia.bind("<Button-1>", lambda event: calendar("give", dia))
                semana = crear_label(x, 'Semana', 300,260, 350, 50)
                semana.bind("<Button-1>", lambda event: futuro(7,"b"))
                mes = crear_label(x, 'Mes', 300,330, 350, 50)
                mes.bind("<Button-1>", lambda event: futuro(30,"b"))
                elementos_actuales.extend([etiqueta,dia,semana,mes])

        elif target == "medicamento":
            if usuario_actual == "admin":
                registrar = crear_label(x, 'Registrar %s' % target, 300,190, 350, 50)
                registrar.bind("<Button-1>", lambda event: ventana_registro(target))
                eliminar = crear_label(x, 'Eliminar %s' % target, 300,260, 350, 50)
                eliminar.bind("<Button-1>", lambda event: ventana_eliminar(target))
                ver = crear_label(x, 'Ver medicamento', 300,330, 350, 50)
                ver.bind("<Button-1>", lambda event: ventana_eliminar(target))
                elementos_actuales.extend([registrar, eliminar, ver])
        elif target == "paciente" and usuario_actual == "doctor":
            futuro(7, "a")
        else:
            registrar = crear_label(x, 'Registrar %s' % target, 300,120, 350, 50)
            registrar.bind("<Button-1>", lambda event: ventana_registro(target))
            eliminar = crear_label(x, 'Eliminar %s' % target, 300,190, 350, 50)
            eliminar.bind("<Button-1>", lambda event: ventana_eliminar(target))
            modificar = crear_label(x, 'Modificar %s' % target, 300,260, 350, 50)
            modificar.bind("<Button-1>", lambda event: elegir(target))
            ver = crear_label(x, 'Ver %s' % target, 300,330, 350, 50)
            ver.bind("<Button-1>", lambda event: ventana_ver(target))

            if target == "doctor":
                visualizar = crear_label(x, 'Visualizar %ses' % target, 300, 400, 350, 50)
            else:
                visualizar = crear_label(x, 'Visualizar %ss' % target, 300, 400, 350, 50)

            visualizar.bind("<Button-1>", lambda event: visualizar_tabla(target))
            elementos_actuales.extend([registrar, eliminar, modificar, ver, visualizar])

    def consulta(a):
        limpiar_pantalla()
        def guardarConsulta():
            texto = entrada_texto.get("1.0", "end-1c")
            selecc = str(seleccionar.cget("text"))
            if texto == "" or selecc == "Seleccionar":
                messagebox.showinfo("Error", "Favor de llenar los campos")
                return
            conexion = conectar_base()
            if conexion:
                cursor = conexion.cursor()
                try:
                    nombre = None
                    for clave, valor in listaMedicamento.items():
                        if valor == selecc:
                            nombre = clave
                            nombre2 = valor
                    cursor.execute("""
                        INSERT INTO consulta (codigo, codigo_cita, diagnostico, codigo_medicamento)
                        VALUES (%s, %s, %s, %s)""",
                        (codigo, a[0], texto, nombre))
                    conexion.commit()
                    messagebox.showinfo("Registro exitoso", "¡Registrado con éxito!")
                    limpiar_pantalla()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {e}")
                finally:
                    i = 0
                    lista = []
                    for item in a:
                        lista.extend([str(item)])

                    crear_pdf(lista, texto, nombre2)
                    #pdf_file = "Consulta_Medica.pdf"
                    cursor.close()
                    conexion.close()

        if len(listaConsultas)>0:
            codigo = max(listaConsultas) + 1
        else:
            codigo = 1
        etiqueta = crear_texto(frame, 'Ingrese el diagnóstico:', 230,100, 400, 50,20)
        entrada_texto = tk.Text(frame,bg="#DCDCCF", font=("Arial", 12))
        entrada_texto.place(x=200, y=150, width=560, height=100)
        seleccionar = crear_label(frame, 'Seleccionar medicamento', 300,270, 350, 50)
        seleccionar.config(font=(12))
        seleccionar.bind("<Button-1>", lambda event: mostrar_opciones(frame, "medicamento", 300, 320, seleccionar))
        boton = crear_label(frame, 'Aceptar', 300,370, 350, 50)
        boton.bind("<Button-1>", lambda event: guardarConsulta())
        elementos_actuales.extend([entrada_texto,seleccionar,boton])

    def registrar_cita(frame, target, who):
        datos = []
        quien = None
        limpiar_pantalla()

        def mostrar_horas(posx,posy,label):
            if dia_elegido == None or cod_paciente.cget("text") == '' or cod_doctor.cget("text") == '':
                messagebox.showinfo("Error", "Favor de llenar los campos anteriores")
                return
            conectar = conectar_base()
            if conectar:
                cursor = conectar.cursor()
            for item in elementos_actuales:
                if isinstance(item, tk.Listbox):
                    item.destroy()
            def seleccionar(event):
                seleccion = listbox.curselection()
                if seleccion:

                    item = str(listbox.get(seleccion))
                    label.configure(text=item, font = ("helvetica", 10))
                    listbox.destroy()
            listbox = tk.Listbox(frame,height=0, width=20, bg="#E5E1D7")
            index = 0
            for clave, valor in listaDoctores.items():
                if valor == cod_doctor.cget("text"):
                    nombre = clave
            for i in range(9, 21):
                listbox.insert(tk.END, ("%s:00"%i))
                listbox.bind("<<ListboxSelect>>", seleccionar)

                cursor.execute("SELECT * FROM cita WHERE fecha=%s AND hora=%s AND codigo_doctor=%s", (str(dia_elegido), str("%s:00:00" % i), str(nombre)))
                if cursor.fetchone():
                    listbox.itemconfig(index, {'bg':'#da627c'})
                listbox.place(x = posx, y = posy+10)
                elementos_actuales.extend([listbox])
                index+=1      

        def guardar_en_base():
            conexion = conectar_base()
            global dia_elegido
            if dia_elegido == None or cod_paciente.cget("text") == '' or cod_doctor.cget("text") == '' or hora.cget("text") == '':
                messagebox.showinfo("Error", "Favor de llenar todos los campos")
                return
            horaLen = len(str(hora.cget("text")))
            horaReal = None
            if horaLen == 0:
                messagebox.showinfo("Error", "Favor de llenar la hora")
                return
            elif horaLen == 5:
                horaReal = str(hora.cget("text")) + ":00"
            else:
                horaReal = str(hora.cget("text"))
            
            datos.clear()
            fecha = str(dia_elegido)
            datos.extend([fecha,horaReal])
            for clave, valor in listaDoctores.items():
                if valor == cod_doctor.cget("text"):
                    datos.extend([str(clave)])
            for clave, valor in listaPacientes.items():
                if valor == cod_paciente.cget("text"):
                    datos.extend([str(clave)])
            if conexion:
                cursor = conexion.cursor()
                try:
                    print(datos)
                    cursor.execute("SELECT * FROM cita WHERE fecha=%s AND hora=%s AND codigo_doctor=%s", (dia_elegido,datos[1],datos[2]))
                    if cursor.fetchone():
                        messagebox.showinfo("Error", "El doctor tiene esa fecha ocupada")
                        datos.clear()
                        return

                    # Inserción en la base de datos
                    if target == "registrar":
                        cursor.execute("""
                            INSERT INTO cita (codigo, codigo_paciente, codigo_doctor, \
                                fecha, hora)
                            VALUES (%s, %s, %s, %s, %s)
                            """, (codigo, datos[3],datos[2],datos[0],datos[1]))
                        
                        
                        conexion.commit()
                    else:
                        cursor.execute("""UPDATE cita SET codigo_paciente=%s, codigo_doctor=%s, fecha=%s, hora=%s WHERE codigo=%s""", (datos[3],datos[2],datos[0],datos[1],codigo))
                        conexion.commit()     

                    messagebox.showinfo("Registro exitoso", "¡Cita registrada con éxito!")
                    limpiar_pantalla()
                #except Exception as e:
                 #   messagebox.showerror("Error", f"Error al registrar cita: {e}")
                finally:
                    cursor.execute("SELECT * FROM cita ORDER BY codigo;")
                    cursor.close()
                    conexion.close()
        if len(listaCitas)>0:
            codigo = max(listaCitas) + 1
        else:
            codigo = 1
        
        cod_doctor = crear_label(frame, '', 320,140, 250, 24)
        cod_doctor.config(font=(10))
        cod_doctor.bind("<Button-1>", lambda event: mostrar_opciones(frame, "doctor", 320, 160, cod_doctor))
        cod_paciente = crear_label(frame, '', 320,180, 250, 24)
        cod_paciente.config(font=(10))
        cod_paciente.bind("<Button-1>", lambda event: mostrar_opciones(frame, "paciente", 320, 200, cod_paciente))
        fecha = crear_label(frame, '', 320,220, 130, 24)
        fecha.config(font=(10))
        fecha.bind("<Button-1>", lambda event: calendar("get", fecha))
        hora = crear_label(frame, "", 320,260, 130, 24)
        hora.config(font=(10))
        hora.bind("<Button-1>",lambda event: mostrar_horas(320, 280, hora))

        save = crear_label(x, "Guardar", 660, 250, 100, 80)
        save.config(font=(15))
        save.bind("<Button-1>", lambda event: guardar_en_base())
        elementos_actuales.extend([cod_paciente, cod_doctor, fecha, hora, save])
        startPoint = 140
        lista = ["Doctor", "Paciente", "Fecha", "Hora"]
        for i in lista:
            crear_texto(frame, i, 180, startPoint, 120,24, 15)
            startPoint += 40

        if target == "modificar":
            conexion = conectar_base()
            if conexion:
                cursor = conexion.cursor()
                try:
                    datos.clear()
                    codigo = int(who)
                    who = str(who)
                    cursor.execute("SELECT * FROM cita WHERE codigo=%s", (who))
                    quien = cursor.fetchone()
                    doctor = listaDoctores[int(quien[2])]
                    cod_doctor.config(text=doctor,font = ("helvetica", 10))
                    paciente = listaPacientes[int(quien[1])]
                    cod_paciente.config(text=paciente,font = ("helvetica", 10))
                    global dia_elegido
                    fecha2 = str(quien[3])
                    dia_elegido = fecha2
                    print(fecha2)
                    fecha.config(text=quien[3])
                    hora.config(text=quien[4],font = ("helvetica", 10))
                    codigo = int(who)
                    horaReal = str(hora.cget("text"))
                    datos.extend([])
                    datos.extend([fecha2,horaReal])
                    for clave, valor in listaDoctores.items():
                        if valor == cod_doctor.cget("text"):
                            datos.extend([str(clave)])
                    for clave, valor in listaPacientes.items():
                        if valor == cod_paciente.cget("text"):
                            datos.extend([str(clave)])
                        
                finally:
                    cursor.close()
                    conexion.close()
            etiqueta = crear_texto(frame, 'Modificar cita %s'%who[0], 240,100, 350, 40,20)
            elementos_actuales.extend([etiqueta])
        else:
            etiqueta = crear_texto(frame, 'Registrar cita %s'%codigo, 240,100, 350, 40,20)
            elementos_actuales.extend([etiqueta])


    def calendar(type, label):
        ventana_calendario = Toplevel(x)
        ventana_calendario.geometry("300x270")
        ventana_calendario.title("Calendario de Eventos")

        def elegir_dia():
            fecha_elegida = cal.selection_get()
            if type == "give":
                visualizar_cita("dia", fecha_elegida, 0,"b")
            else:
                global dia_elegido
                dia_elegido = fecha_elegida
                label.config(text=fecha_elegida, font=("helvetica",10))
            ventana_calendario.destroy()

        frame_calendario = Frame(ventana_calendario)
        frame_calendario.grid(row=0, column=0, padx=10, pady=10)
        cal = Calendar(frame_calendario, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        boton_visualizar = tk.Button(frame_calendario, text="Elegir", command=elegir_dia)
        boton_visualizar.grid(row=1, column=0, columnspan=2, pady=10)
    
    def futuro(tiempo, button):
        fecha = datetime.now().date()
        fecha_futura = fecha + timedelta(days=tiempo)
        f1 = str(fecha)
        f2 = str(fecha_futura)

        visualizar_cita(tiempo, f1,f2, button)

    def visualizar_cita(tiempo, fecha, fecha_futura, button):
        conectar = conectar_base()
        if conectar:
            cursor = conectar.cursor()
            try:
                if tiempo == "todo":
                    cursor.execute("SELECT * FROM cita ORDER BY codigo;")
                elif tiempo == "dia":
                    fecha2 = str(fecha)
                    cursor.execute("""SELECT * FROM cita WHERE fecha=%s AND codigo_doctor=%s ORDER BY codigo""",(fecha2,nombre_usuario[0]))
                elif isinstance(tiempo, int):
                    cursor.execute("""SELECT * FROM cita WHERE codigo_doctor=%s and fecha BETWEEN %s AND %s ORDER BY codigo""", (nombre_usuario[0], fecha, fecha_futura))

                citas = cursor.fetchall()
                ventana_visualizar = Toplevel()
                ventana_visualizar.geometry("650x300")
                ventana_visualizar.title("Visualizar citas")
                # Crear Treeview para la tabla
                tabla = ttk.Treeview(ventana_visualizar, columns=("Código", "Paciente", "Doctor", "Fecha", "Hora"), show="headings")
                columnas = [("Código", 50), ("Paciente", 200), ("Doctor", 200), ("Fecha", 80),("Hora", 80)]
                for col, ancho in columnas:
                    tabla.heading(col, text=col)
                    tabla.column(col, width=ancho, anchor="center")  

                for cita in citas:
                    if usuario_actual == "admin":
                        tabla.insert("", tk.END, values=(cita[0], listaPacientes[int(cita[1])], listaDoctores[int(cita[2])], cita[3], cita[4]))
                    else:

                        tabla.insert("", tk.END, values=(cita[0], listaPacientes[int(cita[1])], listaDoctores[int(cita[2])], cita[3], cita[4]))

                tabla.pack(pady=10, padx=10)

                def consultar():
                    seleccionado = tabla.selection()
                    if seleccionado:
                        valores = tabla.item(seleccionado, "values")
                        consulta(valores)
                        ventana_visualizar.destroy()
                        print(valores)
                    else:
                        messagebox.showwarning("Selección vacía", "No se ha seleccionado ninguna fila.")
                
                if button == "a":
                    buton = tk.Label(ventana_visualizar, text="Consultar")
                    buton.pack(padx=10, pady = 10)
                    buton.bind("<Button-1>", lambda event: consultar())
            finally:
                cursor.close()
                conectar.close()

    def eliminar_cita():
        limpiar_pantalla()
        def eliminacion():
            conexion = conectar_base()
            if conexion:
                cursor = conexion.cursor()
                try:
                    codigo_ingresado = codigo.get()
                    if not codigo_ingresado.isdigit():
                        messagebox.showinfo("Error", "El código no es valido")
                        return
                    cursor.execute("SELECT * FROM cita WHERE codigo=%s", (codigo_ingresado))
                    if cursor.fetchone():
                        cursor.execute("DELETE FROM cita WHERE codigo = %s;", (codigo_ingresado))
                        messagebox.showinfo("Eliminación exitosa", "¡Eliminado con éxito!")
                        limpiar_pantalla()
                    else:
                        messagebox.showinfo("Error", "El código no existe")
                    conexion.commit()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {e}")
                finally:
                    cursor.close()
                    conexion.close()
        etiqueta = crear_texto(frame, 'Ingrese el código de la cita', 185,190, 470, 50,20)
        codigo = crear_entry(frame, '', 350,260, 20, 50)
        boton = crear_label(frame, 'Eliminar', 300,330, 350, 50)
        boton.bind("<Button-1>", lambda event: eliminacion())
        elementos_actuales.extend([etiqueta,codigo,boton])

    def visualizar_calendario(target):
        ventana_calendario = Toplevel(x)
        ventana_calendario.geometry("300x300")
        ventana_calendario.title("Calendario de Eventos")

        conexion = conectar_base()
        cursor = conexion.cursor()
        cursor.execute("SELECT DISTINCT fecha FROM cita")
        fechas_con_eventos = cursor.fetchall()
        conexion.close()

        frame_calendario = Frame(ventana_calendario)
        frame_calendario.grid(row=0, column=0, padx=10, pady=10)
        global cal
        cal = Calendar(frame_calendario, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        for (fecha,) in fechas_con_eventos:
            cal.calevent_create(fecha, 'Evento', 'evento')
        cal.tag_config('evento', background='lightblue', foreground='black')
        boton_visualizar = tk.Button(frame_calendario, text="Visualizar Eventos", command=visualizar_eventos)
        boton_visualizar.grid(row=1, column=0, columnspan=2, pady=10) 

    def visualizar_eventos():
        fecha = cal.selection_get()
        conexion = conectar_base()
        cursor = conexion.cursor()
        cursor.execute("SELECT hora, codigo, codigo_paciente, codigo_doctor FROM cita WHERE fecha = %s ORDER BY hora", (fecha,))
        eventos = cursor.fetchall()
        conexion.close()

        if eventos:
            eventos_texto = "\n".join([f"Hora: {evento[0]}, codigo: {evento[1]}, codigo_paciente: {evento[2]}, codigo_doctor: {evento[3]}" for evento in eventos])
            messagebox.showinfo("Eventos", eventos_texto)
        else:
            messagebox.showinfo("Eventos", "No hay eventos programados para esta fecha.")
    #//////////////////////////////////////////////////////////////////////////////////////
    
    def visualizar_tabla(target):
        conectar = conectar_base()
        if conectar:
            cursor = conectar.cursor()
            try:
                ventana_visualizar = Toplevel()
                ventana_visualizar.geometry("1140x400")
                ventana_visualizar.title("Visualizar %ss"%target)
                frame_tabla = Frame(ventana_visualizar)
                frame_tabla.pack(fill="both", expand=True)
                style = ttk.Style()
                style.configure("Treeview", font=("Helvetica", 8))  # Configura la fuente de la tabla
                style.configure("Treeview.Heading", font=("Helvetica", 8, "bold"))
                # Crear Treeview para la tabla

                if target == "empleado":
                    tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Dirección", "Teléfono", "Fecha de Nacimiento", "Sexo",
                                                                   "Sueldo", "Turno", "Contraseña"), show="headings")
                    columnas = [
                        ("Código", 50), ("Nombre", 230), ("Dirección", 230), ("Teléfono", 90),
                        ("Fecha de Nacimiento", 150), ("Sexo", 90), ("Sueldo", 90), ("Turno", 100),("Contraseña", 80)
                    ]
                    cursor.execute("""SELECT * FROM empleado""")
                    items = cursor.fetchall()
                elif target == "doctor":
                    tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Dirección", "Teléfono", "Fecha de Nacimiento", "Sexo",
                                                                   "Especialidad", "Contraseña"), show="headings")
                    columnas = [
                        ("Código", 50), ("Nombre", 230), ("Dirección", 230), ("Teléfono", 90),
                        ("Fecha de Nacimiento", 150), ("Sexo", 90), ("Especialidad", 130), ("Contraseña", 80)
                    ]
                    cursor.execute("""SELECT * FROM doctor""")
                    items = cursor.fetchall()
                elif target == "paciente":
                    tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Dirección", "Teléfono", "Fecha de Nacimiento", "Sexo",
                                                                   "edad", "estatura"), show="headings")
                    columnas = [
                        ("Código", 50), ("Nombre", 230), ("Dirección", 230), ("Teléfono", 90),
                        ("Fecha de Nacimiento", 150), ("Sexo", 90), ("edad", 130), ("estatura", 80)
                    ]
                    cursor.execute("""SELECT * FROM paciente""")
                    items = cursor.fetchall()
                elif target == "medicamento":
                    tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Administración", "Presentación", "Caducidad"), show="headings")
                    columnas = [
                        ("Código", 50), ("Nombre", 230), ("Administración", 150), ("Presentación", 150),
                        ("Caducidad", 90)
                    ]
                    cursor.execute("""SELECT * FROM medicamento""")
                    items = cursor.fetchall()
  
                # Llenar la tabla con los datos de los empleados
                for col, ancho in columnas:
                    tabla.heading(col, text=col)
                    tabla.column(col, width=ancho, anchor="center")  
                for item in items:
                    tabla.insert("", "end", values=item)

                tabla.pack(pady=10, padx=10)
            finally:
                cursor.close()
                conectar.close()
    
    #((((((((((((((((((((((((((((((((((((((((()))))))))))))))))))))))))))))))))))))))))
    def ventana_eliminar(target):
        limpiar_pantalla()
        def eliminacion():
            conexion = conectar_base()
            if conexion:
                cursor = conexion.cursor()
                try:
                    codigo_ingresado = seleccionar.cget("text")
                    if codigo_ingresado == "Seleccionar":
                        messagebox.showinfo("Error", "Seleccione una opción")
                        return
                                 
                    if target == "empleado":
                        for clave, valor in listaEmpleados.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)
                        cursor.execute("SELECT * FROM empleado WHERE codigo=%s", (codigo_ingresado))
                        if cursor.fetchone():
                            cursor.execute("DELETE FROM empleado WHERE codigo = %s;", (codigo_ingresado))
                            messagebox.showinfo("Eliminación exitosa", "¡Eliminado con éxito!")
                            limpiar_pantalla()
                        else:
                            messagebox.showinfo("Error", "El código no existe")
                    elif target == "doctor":
                        for clave, valor in listaDoctores.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)
                        cursor.execute("SELECT * FROM doctor WHERE codigo=%s", (codigo_ingresado))
                        if cursor.fetchone():
                            cursor.execute("DELETE FROM doctor WHERE codigo = %s;", (codigo_ingresado))
                            messagebox.showinfo("Eliminación exitosa", "¡Eliminado con éxito!")
                            limpiar_pantalla()
                    elif target == "medicamento":
                        for clave, valor in listaMedicamento.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)
                        cursor.execute("SELECT * FROM medicamento WHERE codigo=%s", (codigo_ingresado))
                        if cursor.fetchone():
                            cursor.execute("DELETE FROM medicamento WHERE codigo = %s;", (codigo_ingresado))
                            messagebox.showinfo("Eliminación exitosa", "¡Eliminado con éxito!")
                            limpiar_pantalla()
                        else:
                            messagebox.showinfo("Error", "El código no existe")
                    elif target == "paciente":
                        for clave, valor in listaPacientes.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)

                        cursor.execute("SELECT * FROM paciente WHERE codigo=%s", (codigo_ingresado))
                        if cursor.fetchone():
                            cursor.execute("DELETE FROM paciente WHERE codigo = %s;", (codigo_ingresado))
                            messagebox.showinfo("Eliminación exitosa", "¡Eliminado con éxito!")
                            limpiar_pantalla()
                        else:
                            messagebox.showinfo("Error", "El código no existe")
                    conexion.commit()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {e}")
                finally:
                    cursor.close()
                    conexion.close()
        etiqueta = crear_texto(frame, 'Seleccione el nombre del %s' %target, 240,100, 470, 50,20)
        seleccionar = crear_label(frame, 'Seleccionar', 300,160, 350, 50)
        seleccionar.bind("<Button-1>", lambda event: mostrar_opciones(frame, target, 300, 210, seleccionar))
        #codigo = crear_entry(frame, '', 350,260, 20, 50) antiguo modulo de insertar codigo
        boton = crear_label(frame, 'Eliminar', 300,330, 350, 50)
        boton.config(bg="#da627c")
        boton.bind("<Button-1>", lambda event: eliminacion())
        elementos_actuales.extend([etiqueta,seleccionar,boton])
    
    #-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-
    def elegir(target):
        limpiar_pantalla()
        if target == "cita":
            etiqueta = crear_texto(frame, 'Seleccione el código de la cita', 240,100, 470, 50,20)
        else:
            etiqueta = crear_texto(frame, 'Seleccione el nombre del %s' %target, 240,100, 470, 50,20)
        seleccionar = crear_label(frame, 'Seleccionar', 300,160, 350, 50)
        seleccionar.bind("<Button-1>", lambda event: mostrar_opciones(frame, target, 300, 210, seleccionar))
        #codigo = crear_entry(frame, '', 350,260, 20, 50) antiguo modulo de insertar codigo
        boton = crear_label(frame, 'Modificar', 300,330, 350, 50)
        if target == "cita":
            boton.bind("<Button-1>", lambda event: registrar_cita(frame, "modificar", seleccionar.cget("text")))
        else:
            boton.bind("<Button-1>", lambda event: ventana_modificar(target, seleccionar.cget("text")))
        elementos_actuales.extend([etiqueta,seleccionar,boton])

    def ventana_modificar(target, who):
        if who == "Seleccionar":
            messagebox.showinfo("Error", "Seleccione una opción")
            return
        limpiar_pantalla()
        def modificar(who):
            conexion = conectar_base()
            if conexion:
                cursor = conexion.cursor()
                try:
                    # Inserción en la base de datos
                    if who == "empleado":
                        cursor.execute("""
                            UPDATE empleado SET codigo = %s, nombre = %s, direccion = %s, telefono = %s, fecha_nac = %s, 
                            sexo = %s, sueldo = %s, turno = %s, contrasena = %s WHERE codigo = %s
                            """, (codigo.get(), nombre.get(), direccion.get(), telefono.get(), 
                            fecha_nac.get(), sexo.get(), sueldo.get(), turno.get(), contrasena.get(), codigo_ingresado))
                    
                    elif who == "doctor":
                        cursor.execute("""
                            UPDATE doctor SET codigo = %s, nombre = %s, direccion = %s, telefono = %s, fecha_nac = %s, 
                            sexo = %s, especialidad = %s, contrasena = %s WHERE codigo = %s
                            """, (codigo.get(), nombre.get(), direccion.get(), telefono.get(), 
                            fecha_nac.get(), sexo.get(), especialidad.get(), contrasena.get(), codigo_ingresado))
                    
                    elif who == "paciente":
                        cursor.execute("""
                            UPDATE paciente SET codigo = %s, nombre = %s, direccion = %s, telefono = %s, fecha_nac = %s, 
                            sexo = %s, edad = %s, estatura = %s WHERE codigo = %s
                            """, (codigo.get(), nombre.get(), direccion.get(), telefono.get(), 
                            fecha_nac.get(), sexo.get(), edad.get(), estatura.get(), codigo_ingresado))                      
                    conexion.commit()
                    messagebox.showinfo("Registro exitoso", "¡Registrado con éxito!")
                    limpiar_pantalla()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {e}")
                finally:
                    cursor.close()
                    conexion.close()

        conectar = conectar_base()
        if conectar:
            cursor = conectar.cursor()
            try:
                if target == "empleado":
                    for clave, valor in listaEmpleados.items():
                        if valor == who:
                            codigo_ingresado = str(clave)

                    cursor.execute("""SELECT * FROM empleado WHERE codigo = %s""", (codigo_ingresado))
                    items = cursor.fetchone()

                elif target == "doctor":
                    for clave, valor in listaDoctores.items():
                        if valor == who:
                            codigo_ingresado = str(clave)

                    cursor.execute("""SELECT * FROM doctor WHERE codigo = %s""", (codigo_ingresado))
                    items = cursor.fetchone()
                    for clave, valor in listaDoctores.items():
                        if valor == codigo_ingresado:
                            codigo_ingresado = str(clave)

                elif target == "paciente":
                    for clave, valor in listaPacientes.items():
                        if valor == who:
                            codigo_ingresado = str(clave)

                    cursor.execute("""SELECT * FROM paciente WHERE codigo = %s""", (codigo_ingresado))
                    items = cursor.fetchone()
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")
            finally:
                cursor.close()
                conectar.close()
        crear_texto(frame, 'Modificar %s'%target, 300, 100, 300, 30, 20)
        codigo = crear_entry(frame, items[0], 320,140, 24, 24)
        nombre = crear_entry(frame, items[1], 320, 180, 24, 24)
        direccion = crear_entry(frame, items[2], 320, 220, 24, 24)
        telefono = crear_entry(frame, items[3], 320, 260, 24, 24)
        fecha_nac = crear_entry(frame, items[4], 320, 300, 24, 24)
        sexo = crear_entry(frame, items[5], 320, 340, 24, 24)

        save = crear_label(x, "Guardar", 660, 250, 100, 80)
        save.config(font=(15))
        save.bind("<Button-1>", lambda event: modificar(target))

        if target == "empleado":
            sueldo = crear_entry(frame, items[6], 320, 380, 24, 24)
            turno = crear_entry(frame, items[7], 320, 420, 24, 24)
            contrasena = crear_entry(frame, items[8], 320, 460, 24, 24)
            elementos_actuales.extend([codigo, nombre, direccion, telefono, fecha_nac, sexo, sueldo, turno, contrasena, save])
            choosen = datosEmpleado
        elif target == "doctor":
            especialidad = crear_entry(frame, items[6], 320, 380, 24, 24)
            contrasena = crear_entry(frame, items[7], 320, 420, 24, 24)
            elementos_actuales.extend([codigo, nombre, direccion, telefono, fecha_nac, sexo, especialidad, contrasena, save])
            choosen = datosDoctor
        elif target == "paciente":
            edad = crear_entry(frame, items[6], 320, 380, 24, 24)
            estatura = crear_entry(frame, items[7], 320, 420, 24, 24)
            elementos_actuales.extend([codigo, nombre, direccion, telefono, fecha_nac, sexo, edad, estatura, save])
            choosen = datosPaciente

        startPoint = 140
        for i in choosen:
            crear_texto(frame, i, 180, startPoint, 120,24, 15)
            startPoint += 40
        
    
    def ventana_ver(target):
        limpiar_pantalla()
        def ver(target):
                
            conectar = conectar_base()
            if conectar:
                cursor = conectar.cursor()
                try:
                    codigo_ingresado = seleccionar.cget("text")
                    if codigo_ingresado == "Seleccionar":
                        messagebox.showinfo("Error", "Seleccione una opción")
                        return
                    ventana_visualizar = Toplevel()
                    ventana_visualizar.geometry("1140x100")
                    ventana_visualizar.title("Visualizar %s"%target)
                    frame_tabla = Frame(ventana_visualizar)
                    frame_tabla.pack(fill="both", expand=True)
                    style = ttk.Style()
                    style.configure("Treeview", font=("Helvetica", 8))
                    style.configure("Treeview.Heading", font=("Helvetica", 8, "bold"))

                    if target == "empleado":
                        tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Dirección", "Teléfono", "Fecha de Nacimiento", "Sexo",
                                                                    "Sueldo", "Turno", "Contraseña"), show="headings")
                        columnas = [
                            ("Código", 50), ("Nombre", 230), ("Dirección", 230), ("Teléfono", 90),
                            ("Fecha de Nacimiento", 150), ("Sexo", 90), ("Sueldo", 90), ("Turno", 100),("Contraseña", 80)
                        ]
                        for clave, valor in listaEmpleados.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)
                        cursor.execute("""SELECT * FROM empleado WHERE codigo = %s""", (codigo_ingresado))
                        items = cursor.fetchall()
                    elif target == "doctor":
                        tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Dirección", "Teléfono", "Fecha de Nacimiento", "Sexo",
                                                                    "Especialidad", "Contraseña"), show="headings")
                        columnas = [
                            ("Código", 50), ("Nombre", 230), ("Dirección", 230), ("Teléfono", 90),
                            ("Fecha de Nacimiento", 150), ("Sexo", 90), ("Especialidad", 130), ("Contraseña", 80)
                        ]
                        for clave, valor in listaDoctores.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)
                        cursor.execute("""SELECT * FROM doctor WHERE codigo = %s""", (codigo_ingresado))
                        items = cursor.fetchall()
                    elif target == "paciente":
                        tabla = ttk.Treeview(frame_tabla, columns=("Código", "Nombre", "Dirección", "Teléfono", "Fecha de Nacimiento", "Sexo",
                                                                    "edad", "estatura"), show="headings")
                        columnas = [
                            ("Código", 50), ("Nombre", 230), ("Dirección", 230), ("Teléfono", 90),
                            ("Fecha de Nacimiento", 150), ("Sexo", 90), ("edad", 130), ("estatura", 80)
                        ]
                        for clave, valor in listaPacientes.items():
                            if valor == codigo_ingresado:
                                codigo_ingresado = str(clave)
                        cursor.execute("""SELECT * FROM paciente WHERE codigo = %s""", (codigo_ingresado))
                        items = cursor.fetchall()
    
                    for col, ancho in columnas:
                        tabla.heading(col, text=col)
                        tabla.column(col, width=ancho, anchor="center")  
                    for item in items:
                        tabla.insert("", "end", values=item)

                    tabla.pack(pady=10, padx=10)

                finally:
                    cursor.close()
                    conectar.close()

        etiqueta = crear_texto(frame, 'Seleccione el nombre del %s' %target, 240,100, 470, 50,20)
        seleccionar = crear_label(frame, 'Seleccionar', 300,160, 350, 50)
        seleccionar.bind("<Button-1>", lambda event: mostrar_opciones(frame, target, 300, 210, seleccionar))
        boton = crear_label(frame, 'Ver', 300,330, 350, 50)
        boton.bind("<Button-1>", lambda event: ver(target))
        elementos_actuales.extend([etiqueta,seleccionar,boton])

   #//////////////////////////////////////////////////////////////////////////////////////
    def ventana_registro(target):
        limpiar_pantalla()
        def guardar_en_base(who):
            conexion = conectar_base()
            if conexion:
                cursor = conexion.cursor()
                try:
                    # Inserción en la base de datos
                    if who == "empleado":
                        cursor.execute("""
                            INSERT INTO empleado (codigo, nombre, direccion, \
                                telefono, fecha_nac, sexo, sueldo, turno, contrasena)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (codigo.get(), nombre.get(), direccion.get(), telefono.get(), 
                            fecha_nac.get(), sexo.get(), sueldo.get(), turno.get(), contrasena.get()))
                    
                    elif who == "doctor":
                        cursor.execute("""
                            INSERT INTO doctor (codigo, nombre, direccion, \
                                telefono, fecha_nac, sexo, especialidad, contrasena)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (codigo.get(), nombre.get(), direccion.get(), telefono.get(), 
                            fecha_nac.get(), sexo.get(), especialidad.get(), contrasena.get()))
                    
                    elif who == "paciente":
                        cursor.execute("""
                            INSERT INTO paciente (codigo, nombre, direccion, \
                                telefono, fecha_nac, sexo, edad, estatura)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (codigo.get(), nombre.get(), direccion.get(), telefono.get(), 
                            fecha_nac.get(), sexo.get(), edad.get(), estatura.get()))   
                    elif who == "medicamento":
                        cursor.execute("""
                            INSERT INTO medicamento (codigo, nombre, via, presentacion, caducidad)
                            VALUES (%s, %s, %s, %s, %s)
                            """, (codigo.get(), nombre.get(), via.get(), presentacion.get(), 
                            caducidad.get()))
                    conexion.commit()
                    messagebox.showinfo("Registro exitoso", "¡Registrado con éxito!")
                    limpiar_pantalla()
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar: {e}")
                finally:
                    cursor.close()
                    conexion.close()
            #else:
                #resultado_registro.config(text="Error al conectar con la base de datos", fg="red")

        crear_texto(frame, 'Registrar %s'%target, 320, 100, 290, 30, 20)
        if target == "medicamento":
            codigo = crear_entry(frame, '', 320,140, 24, 24)
            nombre = crear_entry(frame, '', 320, 180, 24, 24)
            via = crear_entry(frame, '', 320, 220, 24, 24)
            presentacion = crear_entry(frame, '', 320, 260, 24, 24)
            caducidad = crear_entry(frame, '', 320, 300, 24, 24)
            choosen = datosMedicamento
            save = crear_label(x, "Guardar", 660, 250, 100, 80)
            save.config(font=(15))
            save.bind("<Button-1>", lambda event: guardar_en_base(target))
            elementos_actuales.extend([codigo, nombre, via, presentacion, caducidad, save])
        else:
                
            codigo = crear_entry(frame, '', 320,140, 24, 24)
            nombre = crear_entry(frame, '', 320, 180, 24, 24)
            direccion = crear_entry(frame, '', 320, 220, 24, 24)
            telefono = crear_entry(frame, '', 320, 260, 24, 24)
            fecha_nac = crear_entry(frame, '', 320, 300, 24, 24)
            sexo = crear_entry(frame, '', 320, 340, 24, 24)

            save = crear_label(x, "Guardar", 660, 250, 100, 80)
            save.config(font=(15))
            save.bind("<Button-1>", lambda event: guardar_en_base(target))

            if target == "empleado":
                sueldo = crear_entry(frame, '', 320, 380, 24, 24)
                turno = crear_entry(frame, '', 320, 420, 24, 24)
                contrasena = crear_entry(frame, '', 320, 460, 24, 24)
                elementos_actuales.extend([codigo, nombre, direccion, telefono, fecha_nac, sexo, sueldo, turno, contrasena, save])
                choosen = datosEmpleado
            elif target == "doctor":
                especialidad = crear_entry(frame, '', 320, 380, 24, 24)
                contrasena = crear_entry(frame, '', 320, 420, 24, 24)
                elementos_actuales.extend([codigo, nombre, direccion, telefono, fecha_nac, sexo, especialidad, contrasena, save])
                choosen = datosDoctor
            elif target == "paciente":
                edad = crear_entry(frame, '', 320, 380, 24, 24)
                estatura = crear_entry(frame, '', 320, 420, 24, 24)
                elementos_actuales.extend([codigo, nombre, direccion, telefono, fecha_nac, sexo, edad, estatura, save])
                choosen = datosPaciente
        startPoint = 140
        for i in choosen:
            crear_texto(frame, i, 180, startPoint, 120,24, 15)
            startPoint += 40

    #................................................

    x = Tk()
    x.geometry("800x500+210+100")
    x.title("Nucleo de Diagnostico")
    x.resizable(False, False)
    
    #image_icon=PhotoImage(file="icono.png")
    #x.iconphoto(False, image_icon)

    # Agregar imagen de fondo
    frame = Frame(x)
    frame.pack(fill=BOTH, expand=True)
    background_image = PhotoImage(file="imagenes/fondo.png")
    if usuario == "admin":
        bienvenida = Label(x, text="Hola, admistrador",fg="white", bg="#2c6670",font=('roboto', 22))
        usuario = crear_label(x, 'Empleados', 10, 160, 150, 50)
        usuario.bind("<Button-1>", lambda event: crear_menu("empleado"))

        doctores = crear_label(x, 'Doctores', 10, 230, 150, 50)
        doctores.bind("<Button-1>", lambda event: crear_menu("doctor"))

        pacientes = crear_label(x, 'Pacientes', 10, 300, 150, 50)
        pacientes.bind("<Button-1>", lambda event: crear_menu("paciente"))

        citas = crear_label(x, 'Citas', 10, 370, 150, 50)
        citas.bind("<Button-1>", lambda event: crear_menu("cita"))

        medicamento = crear_label(x, 'Medicamento', 10, 440, 150, 50)
        medicamento.bind("<Button-1>", lambda event: crear_menu("medicamento"))

    elif usuario == "empleado":
        bienvenida = Label(x, text=f'Hola, {nombre_usuario[1]}',fg="white", bg="#2c6670", font=('roboto', 16, 'bold'))
        
        pacientes = crear_label(x, 'Pacientes', 10, 160, 150, 50)
        pacientes.bind("<Button-1>", lambda event: crear_menu("paciente"))

        citas = crear_label(x, 'Citas', 10, 230, 150, 50)
        citas.bind("<Button-1>", lambda event: crear_menu("cita"))

    elif usuario == "doctor":
        bienvenida = Label(x, text=f'Hola, {nombre_usuario[1]}',fg="white", bg="#2c6670", font=('roboto', 16, 'bold'))
        pacientes = crear_label(x, 'Pacientes', 10, 160, 150, 50)
        pacientes.bind("<Button-1>", lambda event: crear_menu("paciente"))

        citas = crear_label(x, 'Citas', 10, 230, 150, 50)
        citas.bind("<Button-1>", lambda event: crear_menu("cita"))
        
    actualizar_listas()
    
    logOutButton=Label(x, text="Cerrar sesión", bg="#da627c", font=('roboto',12,'bold'))
    logOutButton.bind("<Button-1>", lambda event: cerrar_sesion(x))
    logOutButton.place(x=665,y=20, width=100, height=20)
    fondo_label = Label(frame, image=background_image)
    fondo_label.image = background_image
    fondo_label.pack(fill=BOTH, expand=True)
    bienvenida.place(x=165, y=56, width=463, height=32)

#--------------------------------------------------------------------------------------------
def loginuser():
    global noIntentos, nombre_usuario, usuario_actual
    usuario_ingresado=user.get().strip()
    contraseña=password.get().strip()
    if(usuario_ingresado=="" or contraseña=="") or (usuario_ingresado=="usuario_ingresado" or contraseña=="Contraseña"):
        messagebox.showerror("Error","Por favor, llene los campos")
        return
    if usuario_ingresado == user_admin and contraseña == pass_admin:
        messagebox.showinfo("Correcto","Inicio de sesión correcto")
        root.destroy()
        usuario_actual = "admin"
        nombre_usuario = " "
        sesion_iniciada("admin")
    else:
        if not usuario_ingresado.isdigit():
            messagebox.showerror("Error","Usuario o contraseña incorrectos")
            noIntentos += 1
            print(noIntentos)
            if noIntentos == 3:
                messagebox.showerror("Error","Demasiados intentos, cerrando la aplicación")
                root.destroy()
        conectar = conectar_base()
        if conectar:
            cursor = conectar.cursor()
            try:
                cursor.execute("SELECT * FROM empleado WHERE codigo=%s AND contrasena=%s", (usuario_ingresado, contraseña))
                resultado_empleado = cursor.fetchone()
                cursor.execute("SELECT * FROM doctor WHERE codigo=%s AND contrasena=%s", (usuario_ingresado, contraseña))
                resultado_doctor = cursor.fetchone()
                if resultado_empleado:
                    nombre_usuario = resultado_empleado
                    messagebox.showinfo("Correcto","Inicio de sesión correcto")
                    root.destroy()
                    usuario_actual = "empleado"
                    sesion_iniciada("empleado")
                    return
                elif resultado_doctor:
                    nombre_usuario = resultado_doctor
                    messagebox.showinfo("Correcto","Inicio de sesión correcto")
                    root.destroy()

                    usuario_actual = "doctor"
                    sesion_iniciada("doctor")
                    return
                else:
                    messagebox.showerror("Error","Usuario o contraseña incorrectos")
                    noIntentos += 1
                    print(noIntentos)
                    if noIntentos == 3:
                        messagebox.showerror("Error","Demasiados intentos, cerrando la aplicación")
                        root.destroy()
            except Exception as e:
                print(f'Error al conectar a PostgreSQL {e}')

#--------------------------------------------------------------------------------------------
def iniciar_sesion():
    
    global user, password, root
    #-------------------------------Página principal
    root = Tk()
    root.title("Inicio de sesión")
    root.geometry("1250x700+210+100")
    root.config(bg=background)
    root.resizable(False, False)
    #-------------------------------Fondo
    frame = Frame(root, bg="red")
    frame.pack(fill=Y)
    background_image = PhotoImage(file="imagenes/inicio_sesion.png")
    Label(frame,image=background_image).pack()
    
    def enter(e):
        if e.widget.get()==e.widget.name:
            e.widget.delete(0,'end')
    def leave(e):
        if e.widget.get()=='':
            name = e.widget.name
            e.widget.insert(0, str(name))

    user = crear_entry(frame, 'Usuario', 512, 300, 21, 0)
    user.bind("<FocusIn>", enter)
    user.bind("<FocusOut>", leave)

    password = crear_entry(frame, 'Contraseña', 512, 419, 21, 0, show="*")
    password.bind("<FocusIn>", enter)
    password.bind("<FocusOut>", leave)
    
    def hide():
        
        if password.cget("show") == "":
            eyeButton.config(image=closeeye,activebackground="white")
            password.config(show="*")

        else:
            eyeButton.config(image=openeye,activebackground="white")
            password.config(show="")

    
    openeye = PhotoImage(file="imagenes/abierto.png")
    closeeye = PhotoImage(file="imagenes/cerrado.png")
    eyeButton=Button(frame,image=closeeye,bg="#D9D9D9",bd=0,command=hide)
    eyeButton.place(x=750,y=412)

    loginButton=Button(root,text="INICIAR SESION",bg="#0d48ad",fg="white",width=20,height=1,font=('roboto',18,'bold'),bd=0,command=loginuser)
    loginButton.place(x=473,y=530)

    root.mainloop()
iniciar_sesion()