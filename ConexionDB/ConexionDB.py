import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime
import pymysql

#Clase funciona de forma independiente
# Función para crear un círculo en la esquina superior derecha
def create_circle_image(radius, color, border_color, border_width):
    size = (radius * 2, radius * 2)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((0, 0, size[0] - 1, size[1] - 1), fill=color, outline=border_color, width=border_width)
    return ImageTk.PhotoImage(image)


# Función para actualizar la fecha y hora actual
def actualizar_fecha_hora(lbl_fecha_hora):
    def actualizar():
        fecha_hora_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        lbl_fecha_hora.config(text=fecha_hora_actual)
        ventana.after(1000, actualizar)

    actualizar()


# Funcion para reiniciar la app
def reiniciar_aplicacion():
    ventana.destroy()  # Cierra la ventana actual
    iniciar_aplicacion()  # Vuelve a abrir la ventana principal


# Función para buscar la matrícula en la base de datos
def boton_buscar(num_placa):
    if buscar_en_base_de_datos(num_placa):
        abrir_tercera_ventana(num_placa)
    else:
        abrir_cuarta_ventana()


def buscar_en_base_de_datos(num_placa):
    # Realizar la conexión con la base de datos
    conexion = pymysql.connect(host='localhost', user='root', passwd='1234', db='autoscanid')
    cursor = conexion.cursor()

    # Realizar la consulta
    consulta = "SELECT * FROM Placa WHERE Num_placa = %s"
    cursor.execute(consulta, (num_placa,))
    resultado = cursor.fetchone()

    # Cerrar la conexión
    cursor.close()
    conexion.close()

    # Devolver True si se encuentra la matrícula, False en caso contrario
    return resultado is not None


# Función para abrir la tercera ventana
def abrir_tercera_ventana(num_placa):
    # Realizar la conexión con la base de datos
    conexion = pymysql.connect(host='localhost', user='root', passwd='1234', db='autoscanid')
    cursor = conexion.cursor()

    # Realizar la consulta
    nombre_residente = "SELECT Nombre FROM Vehiculo as v INNER JOIN Residente as r ON v.ID_Residente = r.ID_Residente WHERE v.Num_placa = %s"
    cursor.execute(nombre_residente, (num_placa,))
    resultado = cursor.fetchone()

    # Cerrar la conexión
    cursor.close()
    conexion.close()

    ventana.withdraw()  # Ocultar la ventana actual

    tercera_ventana = tk.Toplevel()
    tercera_ventana.title("Bienvenida")
    tercera_ventana.resizable(width=False, height=False)

    #  Obtenemos el largo y  ancho de la pantalla
    wtotal = ventana.winfo_screenwidth()
    htotal = ventana.winfo_screenheight()

    #  Guardamos el largo y alto de la ventana
    wventana = 755
    hventana = 473

    #  Aplicamos la siguiente formula para calcular donde debería posicionarse
    pwidth = round(wtotal / 2 - wventana / 2)
    pheight = round(htotal / 2 - hventana / 2)

    #  Se lo aplicamos a la geometría de la ventana
    tercera_ventana.geometry(str(wventana) + "x" + str(hventana) + "+" + str(pwidth) + "+" + str(pheight))

    lbl_fecha_hora = tk.Label(tercera_ventana, font=('Arial', 15))
    lbl_fecha_hora.pack(side="top", pady=10)
    actualizar_fecha_hora(lbl_fecha_hora)

    circle_image = create_circle_image(30, "green", "black", 2)
    lblCircle = Label(tercera_ventana, image=circle_image, borderwidth=0)
    lblCircle.place(x=680, y=20)

    lbl_bienvenida = tk.Label(tercera_ventana, text="BIENVENIDO", font=('Arial', 40))
    lbl_bienvenida.pack(expand=True)

    lbl_nombre_usuario = tk.Label(tercera_ventana, text=resultado[0], font=('Arial', 30))
    lbl_nombre_usuario.pack(expand=True)

    tercera_ventana.after(10000, reiniciar_aplicacion)
    tercera_ventana.mainloop()


#Función para abrir la cuarta ventana
def abrir_cuarta_ventana():
    ventana.withdraw()  # Ocultar la ventana actual

    cuarta_ventana = tk.Toplevel()
    cuarta_ventana.title("Rechazado")
    cuarta_ventana.resizable(width=False, height=False)

    #  Obtenemos el largo y  ancho de la pantalla
    wtotal = ventana.winfo_screenwidth()
    htotal = ventana.winfo_screenheight()

    #  Guardamos el largo y alto de la ventana
    wventana = 755
    hventana = 473

    #  Aplicamos la siguiente formula para calcular donde debería posicionarse
    pwidth = round(wtotal/2-wventana/2)
    pheight = round(htotal/2-hventana/2)

    #  Se lo aplicamos a la geometría de la ventana
    cuarta_ventana.geometry(str(wventana)+"x"+str(hventana)+"+"+str(pwidth)+"+"+str(pheight))

    lbl_fecha_hora = tk.Label(cuarta_ventana, font=('Arial', 15))
    lbl_fecha_hora.pack(side="top", pady=10)
    actualizar_fecha_hora(lbl_fecha_hora)

    circle_image = create_circle_image(30, "red", "black", 2)
    lblCircle = Label(cuarta_ventana, image=circle_image, borderwidth=0)
    lblCircle.place(x=680, y=20)

    marco = tk.Frame(cuarta_ventana)
    marco.pack(expand=True, pady=20)

    lbl_bienvenida = tk.Label(marco, text="No identificado", font=('Arial', 40))
    lbl_bienvenida.pack(expand=True)

    instruccion = "No se encontró la matricula mostrada"
    lbl_instruccion = tk.Label(marco, text=instruccion, font=('Arial', 16))
    lbl_instruccion.pack(expand=True, pady=20)

    cuarta_ventana.after(3000, reiniciar_aplicacion)
    cuarta_ventana.mainloop()

# Ventana principal

def iniciar_aplicacion():
    global ventana
    ventana = tk.Tk()
    ventana.title("Lector de placas")

    #  Obtenemos el largo y  ancho de la pantalla
    wtotal = ventana.winfo_screenwidth()
    htotal = ventana.winfo_screenheight()

    #  Guardamos el largo y alto de la ventana
    wventana = 755
    hventana = 473

    #  Aplicamos la siguiente formula para calcular donde debería posicionarse
    pwidth = round(wtotal / 2 - wventana / 2)
    pheight = round(htotal / 2 - hventana / 2)

    #  Se lo aplicamos a la geometría de la ventana
    ventana.geometry(str(wventana) + "x" + str(hventana) + "+" + str(pwidth) + "+" + str(pheight))

    ventana.resizable(width=False, height=False)

    lblInstrucciones = tk.Label(ventana,
                                text="Por favor acerque su vehiculo a la camara para la lectura de sus placas y mantengase quieto",
                                font=('Arial', 12), justify="center", wraplength=450)
    lblInstrucciones.place(relx=0.5, rely=0.1, anchor='n')

    lbl_fecha_hora = tk.Label(ventana, font=('Arial', 15))
    lbl_fecha_hora.place(relx=0.5, rely=0, anchor='n')
    actualizar_fecha_hora(lbl_fecha_hora)

    lblInputImage = Label(ventana)
    lblInputImage.grid(column=0, row=2)

    # Caja de texto donde se inserta manualmente la placa
    entry_placa = Entry(ventana, font=('Arial', 12), width=20)
    entry_placa.place(x=275, y=388)

    boton = tk.Button(ventana, text='Buscar Matricula', height='2', width='28', font=('Arial', 12),
                      command=lambda: boton_buscar(entry_placa.get()), borderwidth=0, relief=tk.RIDGE, bg='gray')
    boton.place(x=265, y=420)

    circle_image = create_circle_image(30, "red", "black", 2)
    lblCircle = Label(ventana, image=circle_image, borderwidth=0)
    lblCircle.place(x=680, y=20)

    ventana.mainloop()


# Llamar a la función para iniciar la aplicación
iniciar_aplicacion()