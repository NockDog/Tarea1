import sqlite3
import time
import os
import msvcrt
from os import system
from Conexion import DB
from sqlite3 import IntegrityError

db = DB()

db.ejecutar_consulta('''
CREATE TABLE IF NOT EXISTS productos (
    codigo TEXT UNIQUE,
    nombre TEXT,
    precio REAL,
    cantidad INTEGER
)
''')

db.ejecutar_consulta('''
CREATE TABLE IF NOT EXISTS ubicacion (
    codigo TEXT UNIQUE,
    bodega TEXT,
    pasillo TEXT,
    estante TEXT
)
''')

db.ejecutar_consulta('''
CREATE TABLE IF NOT EXISTS "historial" (
    fecha TEXT,
    usuario TEXT,
    accion TEXT,
    codigo TEXT,
    descripcion TEXT
)
''')

def getch():
    return msvcrt.getch().decode()

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def clear():
    os.system('cls')

def crear_matriz_productos(num_productos):
    matriz_productos = []
    for _ in range(num_productos):
        while True:
            codigo = input("Ingrese el código del producto: ")
            producto_existente = db.ejecutar_consulta("SELECT nombre FROM productos WHERE codigo=?", (codigo,)).fetchone()
            if producto_existente:
                nombre_producto = producto_existente[0]
                print(f"El código proporcionado ya está en uso en el producto '{nombre_producto}'. Por favor, ingrese otro código.")
            else:
                break

        if not producto_existente:
            nombre = input("Ingrese el nombre del producto: ")
            precio = float(input("Ingrese el precio unitario del producto: "))
            cantidad = int(input("Ingrese la cantidad del producto: "))
            bodega = input("Ingrese la bodega del producto: ")
            pasillo = input("Ingrese el pasillo del producto: ")
            estante = input("Ingrese el estante del producto: ")

            producto = {
                'codigo': codigo,
                'nombre': nombre,
                'precio': precio,
                'cantidad': cantidad,
                'bodega': bodega,
                'pasillo': pasillo,
                'estante': estante
            }

            matriz_productos.append(producto)

            db.ejecutar_consulta("INSERT INTO productos VALUES (?, ?, ?, ?)", (codigo, nombre, precio, cantidad))
            db.ejecutar_consulta("INSERT INTO ubicacion VALUES (?, ?, ?, ?)", (codigo, bodega, pasillo, estante))
            db.ejecutar_consulta("INSERT INTO historial VALUES (?,?,?,?,?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'insercion', codigo, f"Se insertó el producto '{nombre}'"))

            print("Producto registrado con éxito.")

    return matriz_productos

def consultar_productos():
    consulta = "SELECT p.codigo, p.nombre, p.precio, p.cantidad, u.bodega, u.pasillo, u.estante FROM productos p JOIN ubicacion u ON p.codigo = u.codigo"
    resultados = db.ejecutar_consulta(consulta)
    print("{:<10} {:<20} {:<10} {:<10} {:<10} {:<10} {:<10}".format("Código", "Nombre", "Precio (₡)", "Unidades", "Bodega", "Pasillo", "Estante"))
    print("="*80)
    for resultado in resultados:
        codigo = resultado[0]
        nombre = resultado[1]
        precio = "₡{:.2f}".format(resultado[2])
        unidades = resultado[3]
        bodega = resultado[4]
        pasillo = resultado[5]
        estante = resultado[6]
        print("{:<10} {:<20} {:<10} {:<10} {:<10} {:<10} {:<10}".format(codigo, nombre, precio, unidades, bodega, pasillo, estante))

def consulta_especifica():
    codigo = input("Ingrese el código del producto a consultar: ")
    producto = db.ejecutar_consulta("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()
    if producto:
        print("{:<10} {:<20} {:<10} {:<10}".format("Código", "Nombre", "Precio (₡)", "Unidades"))
        print("="*50)
        codigo = producto[0]
        nombre = producto[1]
        precio = "₡{:.2f}".format(producto[2])
        unidades = producto[3]
        print("{:<10} {:<20} {:<10} {:<10}".format(codigo, nombre, precio, unidades))
    else:
        print("Producto no encontrado.")

def modificar_producto():
    codigo = input("Ingrese el código del producto a modificar: ")
    producto = db.ejecutar_consulta("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()
    if producto:
        print(f"¿Qué desea modificar en el producto {producto[1]} con código {producto[0]}?")
        print("\t[1] Nombre")
        print("\t[2] Código")
        print("\t[3] Precio")
        print("\t[4] Cantidad")
        print("\t[5] Cancelar")
        opcion = int(getch())
        if opcion == 1:
            nuevo_nombre = input("Ingrese el nuevo nombre: ")
            db.ejecutar_consulta("UPDATE productos SET nombre=? WHERE codigo=?", (nuevo_nombre, codigo))
            db.ejecutar_consulta("INSERT INTO historial VALUES (?,?,?,?,?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'modificacion', codigo, f"Se modificó el nombre del producto '{producto[1]}' a '{nuevo_nombre}'"))
            print("Nombre modificado con éxito.")
        elif opcion == 2:
            nuevo_codigo = input("Ingrese el nuevo código: ")
            db.ejecutar_consulta("UPDATE productos SET codigo=? WHERE codigo=?", (nuevo_codigo, codigo))
            db.ejecutar_consulta("INSERT INTO historial VALUES (?,?,?,?,?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'modificacion', nuevo_codigo, f"Se modificó el código del producto '{producto[1]}' a '{nuevo_codigo}'"))
            print("Código modificado con éxito.")
        elif opcion == 3:
            nuevo_precio = float(input("Ingrese el nuevo precio: "))
            db.ejecutar_consulta("UPDATE productos SET precio=? WHERE codigo=?", (nuevo_precio, codigo))
            db.ejecutar_consulta("INSERT INTO historial VALUES (?,?,?,?,?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'modificacion', nuevo_precio, f"Se modificó el precio del producto '{producto[1]}' a '{nuevo_precio}'"))
            print("Precio modificado con éxito.")
        elif opcion == 4:
            nueva_cantidad = int(input("Ingrese la nueva cantidad: "))
            db.ejecutar_consulta("UPDATE productos SET cantidad=? WHERE codigo=?", (nueva_cantidad, codigo))
            db.ejecutar_consulta("INSERT INTO historial VALUES (?,?,?,?,?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'modificacion', nueva_cantidad, f"Se modificó la cantidad del producto '{producto[1]}' a '{nueva_cantidad}'"))
            print("Cantidad modificada con éxito.")
        elif opcion == 5:
            print("Operación cancelada.")
        else:
            print("Opción no válida.")
    else:
        print("Producto no encontrado.")

def historial_cambios():
    clear()
    print("{:<20} {:<20} {:<20} {:<20} {:<20}".format("Fecha", "Usuario", "Acción", "Código", "Descripción"))
    print("="*100)
    resultados = db.ejecutar_consulta("SELECT * FROM historial")
    for resultado in resultados:
        fecha = resultado[0]
        usuario = resultado[1]
        accion = resultado[2]
        codigo_producto = resultado[3]
        descripcion = resultado[4]
        print("{:<20} {:<20} {:<20} {:<20} {:<20}".format(fecha, usuario, accion, codigo_producto, descripcion))

def confirmar_transaccion(producto, tipo_transaccion):
    while True:
        clear()
        nombre = producto['nombre']
        cantidad_disponible = producto['cantidad']
        if tipo_transaccion == 'retiro':
            print(f"¿Estás seguro que quieres retirar el producto {nombre}? Hay {cantidad_disponible} unidades disponibles.")
        elif tipo_transaccion == 'adicion':
            print(f"¿Estás seguro que quieres adicionar al producto {nombre}? Hay {cantidad_disponible} unidades disponibles.")
        print("\t[1] Continuar")
        print("\t[2] Reintentar")
        print("\t[3] Cancelar")
        opcion = getch()
        if is_number(opcion):
            opcion = int(opcion)
            if opcion == 1:
                return True
            elif opcion == 2:
                return False
            elif opcion == 3:
                return None
            else:
                print("Opción no válida. Por favor, seleccione una opción válida.")
                time.sleep(1)
        else:
            print("Opción no válida. Por favor, seleccione una opción válida.")
            time.sleep(1)
            
def realizar_traslado():
    codigo = input("Ingrese el código del producto a trasladar: ")
    producto = db.ejecutar_consulta("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()
    if producto:
        nueva_bodega = input(f"Ingrese la nueva bodega del producto {codigo}: ")
        nuevo_pasillo = input(f"Ingrese el nuevo pasillo del producto {codigo}: ")
        nuevo_estante = input(f"Ingrese el nuevo estante del producto {codigo}: ")
        db.ejecutar_consulta("UPDATE ubicacion SET bodega=?, pasillo=?, estante=? WHERE codigo=?", (nueva_bodega, nuevo_pasillo, nuevo_estante, codigo))
        db.ejecutar_consulta("INSERT INTO historial VALUES (?,?,?,?,?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'traslado', codigo, f"Se trasladó el producto '{producto[1]}' a la bodega '{nueva_bodega}', pasillo '{nuevo_pasillo}', estante '{nuevo_estante}'"))
        print("Traslado realizado con éxito.")
    else:
        print("Producto no encontrado.")
def realizar_transaccion(tipo_transaccion):
    if tipo_transaccion == 'retiro':
        codigo = input("Ingrese el código del producto a retirar: ")
        producto = db.ejecutar_consulta("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()
        if producto:
            producto_dict = {'codigo': producto[0], 'nombre': producto[1], 'precio': producto[2], 'cantidad': producto[3]}
            cantidad_disponible = producto[3]
            if cantidad_disponible > 0:
                if confirmar_transaccion(producto_dict, tipo_transaccion):
                    cantidad_retirar = int(input("Ingrese la cantidad a retirar: "))
                    if cantidad_disponible >= cantidad_retirar:
                        cantidad_actualizada = cantidad_disponible - cantidad_retirar
                        db.ejecutar_consulta("UPDATE productos SET cantidad=? WHERE codigo=?", (cantidad_actualizada, codigo))
                        db.ejecutar_consulta("INSERT INTO historial (fecha, usuario, accion, codigo, descripcion) VALUES (?, ?, ?, ?, ?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'retiro', codigo, f"Se realizó un retiro de {cantidad_retirar} unidades del producto '{producto[1]}'"))
                        print("Retiro realizado con éxito.")
                    else:
                        print("No hay suficiente cantidad disponible para retirar.")
            else:
                print("No hay unidades disponibles para retirar.")
        else:
            print("Producto no encontrado.")

    elif tipo_transaccion == 'adicion':
        codigo = input("Ingrese el código del producto a adicionar: ")
        producto = db.ejecutar_consulta("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()
        if producto:
            producto_dict = {'codigo': producto[0], 'nombre': producto[1], 'precio': producto[2], 'cantidad': producto[3]}
            if confirmar_transaccion(producto_dict, tipo_transaccion):
                cantidad_adicionar = int(input("Ingrese la cantidad a adicionar: "))
                nueva_cantidad = producto[3] + cantidad_adicionar
                db.ejecutar_consulta("UPDATE productos SET cantidad=? WHERE codigo=?", (nueva_cantidad, codigo))
                db.ejecutar_consulta("INSERT INTO historial (fecha, usuario, accion, codigo, descripcion) VALUES (?, ?, ?, ?, ?)", (time.strftime("%Y-%m-%d %H:%M:%S"), nombre_usuario, 'adicion', codigo, f"Se realizó una adición de {cantidad_adicionar} unidades al producto '{producto[1]}'"))
                print("Adición realizada con éxito.")
            else:
                print("Operación cancelada.")
        else:
            print("Producto no encontrado.")


nombre_usuario = input("Ingrese su nombre: ")

while True:
    clear()
    print("*********************************")
    print("\tCRUD con SQLite3")
    print("*********************************")
    print("\t[1] Insertar un Producto.")
    print("\t[2] Consultar los Productos.")
    print("\t[3] Realizar un Traslado.")
    print("\t[4] Modificar Producto Existente.")
    print("\t[5] Realizar una Transacción.")
    print("\t[6] Ver Historial de Cambios.")
    print("\t[7] Salir del Sistema.")
    print("*********************************")
    try:
        opcion = int(getch())
        if opcion == 1:
            clear()
            num_productos = int(input("Ingrese la cantidad de productos a registrar: "))
            crear_matriz_productos(num_productos)
            time.sleep(1)
        elif opcion == 2:
            clear()
            consultar_productos()
            input("Presione Enter para continuar...")
            clear()
            time.sleep(1)
        elif opcion == 3:
            clear()
            realizar_traslado()
            time.sleep(1)
        elif opcion == 4:
            clear()
            modificar_producto()
            input("Presione Enter para continuar...")
            clear()
            time.sleep(1)
        elif opcion == 5:
            clear()
            print("Seleccione el tipo de transacción:")
            print("\t[1] Retiro")
            print("\t[2] Adición")
            print("\t[3] Consulta Específica")
            tipo_transaccion = getch()
            if is_number(tipo_transaccion):
                tipo_transaccion = int(tipo_transaccion)
                if tipo_transaccion == 1:
                    realizar_transaccion('retiro')
                elif tipo_transaccion == 2:
                    realizar_transaccion('adicion')
                elif tipo_transaccion == 3:
                    consulta_especifica()
                else:
                    print("Opción no válida.")
                time.sleep(1)
            else:
                print("Opción no válida.")
        elif opcion == 6:
            clear()
            historial_cambios()
            input("Presione Enter para continuar...")
            clear()
            time.sleep(1)
        elif opcion == 7:
            clear()
            break
        else:
            print("Opción no válida.")
    except ValueError:
        print("Seleccione una opción correcta.")
        time.sleep(1)