import flet as ft
import json
import os
from datetime import datetime

# Definición de colores principales
COLOR_ROSA_MEXICANO = "#E91E63"
COLOR_LAVANDA = "#9575CD"
COLOR_FONDO = "#FCE4EC"
COLOR_ENCABEZADO = "#C2185B"
COLOR_VERDE = "#81C784"
COLOR_GRIS = "#BDBDBD"

ARCHIVO_DATOS = "datos_patty.json"
ARCHIVO_SESION = "sesion_activa.json"

inventario = {'Concha': 0, 'Frances lagunero': 10, 'Concha nuez': 0, 'Galleta chispas choc': 0, 'Pan de muerto': 0}
precios = {'Concha': 14.0, 'Frances lagunero': 10.0, 'Concha nuez': 17.0, 'Galleta chispas choc': 10.0, 'Pan de muerto': 18.0}
productos_activos = {'Concha': True, 'Frances lagunero': True, 'Concha nuez': True, 'Galleta chispas choc': True, 'Pan de muerto': True}

ventas_totales_cantidad = {producto: 0 for producto in precios}
ventas_totales_dinero = {producto: 0.0 for producto in precios}
suma_total_dinero = 0.0
historial_cortes = []
carrito = []
ultima_venta_realizada = None
pan_activo = {"nombre": None}
inputs_inventario = {}
botones_lista = []

seccion_izq = ft.Column(width=220)
seccion_der = ft.Column(expand=True)
lista_visual = ft.Column()
lista_record = ft.Column()
resultado_total = ft.Text("Total: $0.00", size=18, weight="bold", color="black")
resultado_cambio = ft.Text("Cambio: $0.00", size=18, weight="bold", color="black")
pago_recibido = ft.TextField(label="Efectivo Recibido ($)", width=180, read_only=True)
total_general_visual = ft.Text(value="TOTAL VENDIDO HOY: $0.00", size=16, weight="bold", color="black")

def main(page: ft.Page):
    page.title = "Sistema PATTY - Control Total"
    page.theme_mode = "light"
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO

    def ejecutar_corte(e):
        global suma_total_dinero, ultima_venta_realizada
        if suma_total_dinero > 0:
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            historial_cortes.append({"fecha": fecha_actual, "total": suma_total_dinero})
        suma_total_dinero = 0.0
        ultima_venta_realizada = None
        for pan in precios:
            ventas_totales_cantidad[pan] = 0
            ventas_totales_dinero[pan] = 0.0
        actualizar_lista_record()
        guardar_datos()
        dlg_confirmacion.open = False
        page.update()

    dlg_confirmacion = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Corte"),
        content=ft.Text("¿Borrar todas las ventas del día?"),
        actions=[
            ft.TextButton("Sí", on_click=ejecutar_corte),
            ft.TextButton("No", on_click=lambda e: setattr(dlg_confirmacion, "open", False) or page.update())
        ]
    )
    page.overlay.append(dlg_confirmacion)

    def realizar_corte_click(e):
        dlg_confirmacion.open = True
        page.update()

    def teclado_presionada(e):
        valor = e.control.content.value
        if valor == "C":
            pago_recibido.value = ""
        elif valor == "OK":
            contenedor_teclado.visible = False
        else:
            pago_recibido.value += str(valor)
        calcular_cambio()
        page.update()

    def crear_boton_t(val):
        color_f = COLOR_ROSA_MEXICANO if val=="C" else (COLOR_VERDE if val=="OK" else "white")
        return ft.Button(
            content=ft.Text(val, color="white" if color_f != "white" else "black"),
            on_click=teclado_presionada,
            width=50,
            bgcolor=color_f
        )

    contenedor_teclado = ft.Container(content=ft.Column([
        ft.Row([crear_boton_t("1"), crear_boton_t("2"), crear_boton_t("3")], alignment="center"),
        ft.Row([crear_boton_t("4"), crear_boton_t("5"), crear_boton_t("6")], alignment="center"),
        ft.Row([crear_boton_t("7"), crear_boton_t("8"), crear_boton_t("9")], alignment="center"),
        ft.Row([crear_boton_t("0"), crear_boton_t("C"), crear_boton_t("OK")], alignment="center")
    ], alignment="center"), visible=False, padding=5, bgcolor="white")

    pago_recibido.on_click = lambda e: setattr(contenedor_teclado, "visible", True) or page.update()
    pago_recibido.on_focus = lambda e: setattr(contenedor_teclado, "visible", True) or page.update()

    def guardar_datos():
        datos = {
            "inventario": inventario,
            "ventas_cantidad": ventas_totales_cantidad,
            "ventas_dinero": ventas_totales_dinero,
            "suma_total": suma_total_dinero,
            "historial_cortes": historial_cortes,
            "productos_activos": productos_activos
        }
        try:
            with open(ARCHIVO_DATOS, "w") as f:
                json.dump(datos, f)
        except Exception as ex:
            print(f"Error al guardar datos: {ex}")

    def cargar_datos():
        global suma_total_dinero, historial_cortes
        if os.path.exists(ARCHIVO_DATOS):
            try:
                with open(ARCHIVO_DATOS, "r") as f:
                    d = json.load(f)
                    inventario.update(d.get("inventario", {}))
                    ventas_totales_cantidad.update(d.get("ventas_cantidad", {}))
                    ventas_totales_dinero.update(d.get("ventas_dinero", {}))
                    suma_total_dinero = d.get("suma_total", 0.0)
                    historial_cortes = d.get("historial_cortes", [])
                    productos_activos.update(d.get("productos_activos", {}))
            except Exception as ex:
                print(f"Error al cargar datos: {ex}")

    def verificar_alertas():
        for pan, campo in inputs_inventario.items():
            if inventario[pan] <= 5:
                campo.border_color = "red"
                campo.focused_border_color = "red"
            else:
                campo.border_color = None
                campo.focused_border_color = None
        page.update()

    def actualizar_inventario_desde_inputs(e):
        for pan, input_field in inputs_inventario.items():
            if input_field.value and input_field.value.isdigit():
                inventario[pan] = int(input_field.value)
        guardar_datos()
        verificar_alertas()

    def actualizar_lista_record():
        lista_record.controls.clear()
        lista_record.controls.append(ft.Text("Récord de ventas de hoy:", size=13, weight="bold", color="black"))
        for pan in precios:
            if ventas_totales_cantidad[pan] > 0:
                lista_record.controls.append(
                    ft.Row([
                        ft.Text(f"{pan}:", weight="bold", size=12, color="black"),
                        ft.Text(f"{ventas_totales_cantidad[pan]} pzas | ${ventas_totales_dinero[pan]:.2f}", size=12, color="black")
                    ], alignment="spaceBetween")
                )
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        page.update()

    def procesar_seleccion(n):
        pan = pan_activo["nombre"]
        if pan and inventario[pan] >= n:
            producto = {'pan': pan, 'cant': n, 'subtotal': precios[pan] * n}
            carrito.append(producto)
            fila_item = ft.Row([
                ft.Button("X", on_click=lambda e: eliminar_item(producto, fila_item), bgcolor="#FF5252", color="white", height=30),
                ft.Text(f"{pan} x{n} = ${precios[pan]*n:.2f}", size=12, color="black")
            ], alignment="spaceBetween")
            lista_visual.controls.append(fila_item)
            resultado_total.value = f"Total: ${sum(i['subtotal'] for i in carrito):.2f}"
            seccion_der.controls.clear()
            for b in botones_lista:
                b.bgcolor = COLOR_LAVANDA
                b.content.color = "white"
            page.update()

    def seleccionar_boton(e):
        for b in botones_lista:
            b.bgcolor = COLOR_LAVANDA
            b.content.color = "white"
        e.control.bgcolor = COLOR_ROSA_MEXICANO
        e.control.content.color = "white"
        pan_activo["nombre"] = e.control.content.value
        seccion_der.controls.clear()

        for i in range(1, 11):
            seccion_der.controls.append(
                ft.Button(
                    str(i),
                    on_click=lambda e, n=i: procesar_seleccion(n),
                    width=55, height=33,
                    bgcolor="white",
                    color="black"
                )
            )
        page.update()

    def eliminar_item(producto, fila):
        carrito.remove(producto)
        lista_visual.controls.remove(fila)
        resultado_total.value = f"Total: ${sum(i['subtotal'] for i in carrito):.2f}"
        page.update()

    def confirmar_venta_click(e):
        global suma_total_dinero, ultima_venta_realizada
        if not carrito: return
        
        ultima_venta_realizada = list(carrito)

        for item in carrito:
            inventario[item['pan']] -= item['cant']
            ventas_totales_cantidad[item['pan']] += item['cant']
            ventas_totales_dinero[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
            if item['pan'] in inputs_inventario:
                inputs_inventario[item['pan']].value = str(inventario[item['pan']])

        carrito.clear()
        lista_visual.controls.clear()
        resultado_total.value = "Total: $0.00"
        pago_recibido.value = ""
        resultado_cambio.value = "Cambio: $0.00"
        contenedor_teclado.visible = False
        guardar_datos()
        actualizar_lista_record()
        verificar_alertas()
        page.update()

    def cancelar_ultima_venta(e):
        global suma_total_dinero, ultima_venta_realizada
        if not ultima_venta_realizada:
            page.dialog = ft.AlertDialog(title=ft.Text("No hay ninguna venta reciente para cancelar."))
            page.dialog.open = True
            page.update()
            return

        for item in ultima_venta_realizada:
            inventario[item['pan']] += item['cant'] 
            ventas_totales_cantidad[item['pan']] -= item['cant']
            ventas_totales_dinero[item['pan']] -= item['subtotal']
            suma_total_dinero -= item['subtotal']
            if item['pan'] in inputs_inventario:
                inputs_inventario[item['pan']].value = str(inventario[item['pan']])

        ultima_venta_realizada = None

        guardar_datos()
        actualizar_lista_record()
        verificar_alertas()
        
        page.dialog = ft.AlertDialog(title=ft.Text("¡Última venta cancelada con éxito! Las piezas regresaron al inventario."))
        page.dialog.open = True
        page.update()

    def calcular_cambio(e=None):
        total = sum(i['subtotal'] for i in carrito)
        try:
            pago = float(pago_recibido.value)
            diff = pago - total
            resultado_cambio.value = f"Cambio: ${diff:.2f}" if diff >= 0 else f"Faltan: ${abs(diff):.2f}"
            resultado_cambio.color = "green" if diff >= 0 else "red"
        except:
            resultado_cambio.value = "Cambio: $0.00"
            resultado_cambio.color = "black"
        page.update()

    def crear_bloque(nombre):
        campo_inv = ft.TextField(
            value=str(inventario.get(nombre, 0)),
            width=55, height=40,
            content_padding=5,
            on_change=actualizar_inventario_desde_inputs,
            text_align="center",
            bgcolor="white"
        )
        inputs_inventario[nombre] = campo_inv

        btn = ft.Button(
            content=ft.Text(nombre, size=11, weight="bold", color="white", text_align="center"),
            on_click=seleccionar_boton,
            bgcolor=COLOR_LAVANDA,
            width=132, height=40
        )
        botones_lista.append(btn)
        return ft.Row([campo_inv, btn], alignment="center")

    def cambiar_estado_producto(pan, estado):
        productos_activos[pan] = estado
        guardar_datos()

    def eliminar_corte_historial(corte_item):
        if corte_item in historial_cortes:
            historial_cortes.remove(corte_item)
            guardar_datos()
            cambiar_pantalla("historial")

    def borrar_todo_historial(e):
        historial_cortes.clear()
        guardar_datos()
        cambiar_pantalla("historial")

    def cambiar_pantalla(destino):
        page.controls.clear()
        header = ft.Container(
            content=ft.Text("Pan Casero PATTY", size=20, weight="bold", color="white", text_align="center"),
            bgcolor=COLOR_ENCABEZADO, padding=10, width=float('inf')
        )
        page.add(header)

        if destino == "sistema":
            iniciar_sistema(False)
        elif destino == "opciones":
            checkboxes_col = [ft.Text("Selecciona los productos disponibles hoy:", size=15, weight="bold")]
            for pan in precios.keys():
                chk = ft.Checkbox(
                    label=pan,
                    value=productos_activos.get(pan, True),
                    on_change=lambda e, p=pan: cambiar_estado_producto(p, e.control.value)
                )
                checkboxes_col.append(chk)

            reinversion_hoy = suma_total_dinero * 0.50
            ganancia_hoy = suma_total_dinero * 0.50

            page.add(ft.Container(content=ft.Column([
                ft.Text(f"Total Vendido Hoy: ${suma_total_dinero:.2f}", size=18, weight="bold"),
                ft.Text(f"50% Reinversión: ${reinversion_hoy:.2f}", size=14, weight="bold", color="#00B0FF"),
                ft.Text(f"50% Ganancia Total: ${ganancia_hoy:.2f}", size=14, weight="bold", color="#00C853"),
                ft.Divider(),
                *checkboxes_col,
                ft.Container(height=20),
                ft.Button("VER HISTORIAL DE CORTES", on_click=lambda e: cambiar_pantalla("historial"), bgcolor=COLOR_ROSA_MEXICANO, color="white"),
                ft.Container(height=5),
                ft.Button("VOLVER AL SISTEMA", on_click=lambda e: cambiar_pantalla("sistema"), bgcolor=COLOR_LAVANDA, color="white")
            ], alignment="center", horizontal_alignment="center", scroll=ft.ScrollMode.AUTO), padding=20))

        elif destino == "historial":
            historial_items = []
            if historial_cortes:
                for corte in historial_cortes:
                    reinv = corte['total'] * 0.50
                    gan = corte['total'] * 0.50
                    
                    contenido_tarjeta = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=16),
                                    ft.Text(f"Fecha: {corte['fecha']}", size=13, weight="bold")
                                ], spacing=5),
                                ft.Button("X", on_click=lambda e, ci=corte: eliminar_corte_historial(ci), bgcolor="#FF5252", color="white", width=40, height=30)
                            ], alignment="spaceBetween"),
                            ft.Text(f"Total Corte: ${corte['total']:.2f}", size=14, weight="bold"),
                            ft.Row([
                                ft.Container(width=10, height=10, bgcolor="#00B0FF", border_radius=5),
                                ft.Text(f"Reinversión (50%): ${reinv:.2f}", size=13, color="#00B0FF")
                            ], spacing=5),
                            ft.Row([
                                ft.Container(width=10, height=10, bgcolor="#00C853", border_radius=5),
                                ft.Text(f"Ganancia (50%): ${gan:.2f}", size=13, color="#00C853")
                            ], spacing=5),
                        ], spacing=5),
                        padding=12,
                        bgcolor="white",
                        border_radius=8
                    )
                    
                    marco_tarjeta = ft.Container(
                        content=contenido_tarjeta,
                        bgcolor="#E0E0E0",
                        padding=2,
                        border_radius=10,
                        width=380
                    )
                    historial_items.append(marco_tarjeta)
            else:
                historial_items.append(ft.Text("No hay cortes registrados todavía.", size=13, italic=True))

            page.add(ft.Container(content=ft.Column([
                *historial_items,
                ft.Container(height=15),
                ft.Button("BORRAR TODO EL HISTORIAL", on_click=borrar_todo_historial, bgcolor="#FF5252", color="white"),
                ft.Container(height=5),
                ft.Button("VOLVER A OPCIONES", on_click=lambda e: cambiar_pantalla("opciones"), bgcolor=COLOR_LAVANDA, color="white")
            ], alignment="center", horizontal_alignment="center", scroll=ft.ScrollMode.AUTO), padding=20))

        page.update()

    def iniciar_sistema(es_login=True):
        if es_login:
            try:
                with open(ARCHIVO_SESION, "w") as f: f.write("sesion_iniciada")
            except:
                pass
        cargar_datos()

        botones_lista.clear()
        inputs_inventario.clear()
        seccion_izq.controls.clear()

        elementos_activos = [crear_bloque(p) for p in precios.keys() if productos_activos.get(p, True)]

        seccion_izq.controls.extend(
            elementos_activos +
            [lista_visual, resultado_total, pago_recibido, contenedor_teclado, resultado_cambio,
             ft.Button("CONFIRMAR VENTA", on_click=confirmar_venta_click, bgcolor=COLOR_VERDE, color="white"),
             ft.Button("CANCELAR ÚLTIMA VENTA", on_click=cancelar_ultima_venta, bgcolor="#FF5252", color="white"),
             ft.Button("CORTE", on_click=realizar_corte_click, bgcolor=COLOR_LAVANDA, color="white"),
             lista_record, total_general_visual,
             ft.Button("ADMINISTRACIÓN", on_click=lambda e: cambiar_pantalla("opciones"), bgcolor=COLOR_GRIS, color="white")]
        )

        page.controls.clear()
        header = ft.Container(
            content=ft.Text("Pan Casero PATTY", size=20, weight="bold", color="white", text_align="center"),
            bgcolor=COLOR_ENCABEZADO, padding=10, width=float('inf')
        )
        page.add(header, ft.Row([seccion_izq, seccion_der], expand=True, vertical_alignment=ft.CrossAxisAlignment.START))
        actualizar_lista_record()
        verificar_alertas()
        page.update()

    if os.path.exists(ARCHIVO_SESION):
        iniciar_sistema(False)
    else:
        campo_clave = ft.TextField(label="Clave", password=True, width=200)
        page.add(ft.Column([campo_clave, ft.Button("ENTRAR", on_click=lambda e: iniciar_sistema() if campo_clave.value == "PATTY2026" else None)], alignment="center"))

# Arranque seguro compatible con PC y Celular
if __name__ == "__main__":
    ft.run(main)
