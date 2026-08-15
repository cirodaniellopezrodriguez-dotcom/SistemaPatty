import flet as ft
import json
import os
from datetime import datetime

ARCHIVO_DATOS = "datos_patty.json"
ARCHIVO_SESION = "sesion_activa.json"

inventario = {'Concha': 0, 'Frances lagunero': 0, 'Concha nuez': 0, 'Galleta chispas choc': 0}
precios = {'Concha': 14.0, 'Frances lagunero': 10.0, 'Concha nuez': 17.0, 'Galleta chispas choc': 10.0}
ventas_totales_cantidad = {producto: 0 for producto in precios}
ventas_totales_dinero = {producto: 0.0 for producto in precios}
suma_total_dinero = 0.0
historial_cortes = []
numero_ventas = 0 
carrito = []
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
    page.bgcolor = "#F1C40F" 
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO 

    def ejecutar_corte(e):
        global suma_total_dinero
        if suma_total_dinero > 0:
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            reinversion = suma_total_dinero * 0.50
            ganancia = suma_total_dinero * 0.50
            historial_cortes.append({
                "fecha": fecha_actual, 
                "total": suma_total_dinero,
                "reinversion": reinversion,
                "ganancia": ganancia
            })

        suma_total_dinero = 0.0
        for pan in precios: 
            ventas_totales_cantidad[pan] = 0
            ventas_totales_dinero[pan] = 0.0
        actualizar_lista_record()
        guardar_datos()
        verificar_alertas()
        dlg_confirmacion.open = False
        page.update()

    dlg_confirmacion = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar Corte"),
        content=ft.Text("¿Borrar todas las ventas del día?"),
        actions=[
            ft.TextButton("Sí, realizar corte", on_click=ejecutar_corte),
            ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg_confirmacion, "open", False) or page.update()),
        ],
    )
    page.overlay.append(dlg_confirmacion)

    def realizar_corte_click(e):
        dlg_confirmacion.open = True
        page.update()

    def mostrar_teclado(e):
        contenedor_teclado.visible = True
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
        color_f = "red" if val=="C" else ("green" if val=="OK" else "white")
        return ft.ElevatedButton(content=ft.Text(val, color="white" if color_f != "white" else "black"), on_click=teclado_presionada, width=50, bgcolor=color_f)

    contenedor_teclado = ft.Container(content=ft.Column([
        ft.Row([crear_boton_t("1"), crear_boton_t("2"), crear_boton_t("3")], alignment="center"),
        ft.Row([crear_boton_t("4"), crear_boton_t("5"), crear_boton_t("6")], alignment="center"),
        ft.Row([crear_boton_t("7"), crear_boton_t("8"), crear_boton_t("9")], alignment="center"),
        ft.Row([crear_boton_t("0"), crear_boton_t("C"), crear_boton_t("OK")], alignment="center")
    ], alignment="center"), visible=False, padding=5, bgcolor="white")

    # Vinculamos tanto el click como el foco para asegurar que la calculadora aparezca siempre
    pago_recibido.on_click = mostrar_teclado
    pago_recibido.on_focus = mostrar_teclado

    def guardar_datos():
        datos = {
            "inventario": inventario, 
            "ventas_cantidad": ventas_totales_cantidad, 
            "ventas_dinero": ventas_totales_dinero, 
            "suma_total": suma_total_dinero, 
            "num_ventas": numero_ventas,
            "historial_cortes": historial_cortes
        }
        with open(ARCHIVO_DATOS, "w") as f: json.dump(datos, f)

    def cargar_datos():
        global suma_total_dinero, numero_ventas, historial_cortes
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, "r") as f:
                datos = json.load(f)
                inventario.update(datos.get("inventario", {}))
                ventas_totales_cantidad.update(datos.get("ventas_cantidad", {}))
                ventas_totales_dinero.update(datos.get("ventas_dinero", {}))
                suma_total_dinero = datos.get("suma_total", 0.0)
                numero_ventas = datos.get("num_ventas", 0)
                historial_cortes = datos.get("historial_cortes", [])

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
            if input_field.value and input_field.value.isdigit(): inventario[pan] = int(input_field.value)
        guardar_datos(); verificar_alertas()

    def actualizar_lista_record():
        lista_record.controls.clear()
        for pan in precios:
            if ventas_totales_cantidad[pan] > 0:
                lista_record.controls.append(ft.Row([ft.Text(f"{pan}:", weight="bold", size=12, color="black"), ft.Text(f"{ventas_totales_cantidad[pan]} pzas | ${ventas_totales_dinero[pan]:.2f}", size=12, color="black")], alignment="center"))
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        page.update()

    def procesar_seleccion(n):
        pan = pan_activo["nombre"]
        if pan and inventario[pan] >= n:
            producto = {'pan': pan, 'cant': n, 'subtotal': precios[pan] * n}
            carrito.append(producto)
            fila_item = ft.Row([ft.ElevatedButton("X", on_click=lambda e: eliminar_item(producto, fila_item), bgcolor="red", color="white", height=30), ft.Text(f"{pan} x{n} = ${precios[pan]*n:.2f}", size=12, color="black")], alignment="center")
            lista_visual.controls.append(fila_item)
            resultado_total.value = f"Total: ${sum(i['subtotal'] for i in carrito):.2f}"
            seccion_der.controls.clear()
            for b in botones_lista: b.bgcolor = "green"; b.content.color = "white"
            page.update()

    def seleccionar_boton(e):
        for b in botones_lista: b.bgcolor = "green"; b.content.color = "white"
        e.control.bgcolor = "yellow"; e.control.content.color = "black"
        pan_activo["nombre"] = e.control.content.value
        seccion_der.controls.clear()
        for i in range(1, 11): seccion_der.controls.append(ft.ElevatedButton(str(i), on_click=lambda e, n=i: procesar_seleccion(n), width=50, height=30))
        page.update()

    def eliminar_item(producto, fila):
        carrito.remove(producto); lista_visual.controls.remove(fila)
        resultado_total.value = f"Total: ${sum(i['subtotal'] for i in carrito):.2f}"; page.update()

    def confirmar_venta_click(e):
        global suma_total_dinero
        if not carrito: return
        for item in carrito:
            inventario[item['pan']] -= item['cant']
            ventas_totales_cantidad[item['pan']] += item['cant']
            ventas_totales_dinero[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
            inputs_inventario[item['pan']].value = str(inventario[item['pan']])
        
        carrito.clear()
        lista_visual.controls.clear()
        resultado_total.value = "Total: $0.00"
        pago_recibido.value = ""
        resultado_cambio.value = "Cambio: $0.00"
        resultado_cambio.color = "black"
        contenedor_teclado.visible = False  # Oculta el teclado temporalmente al confirmar
        
        actualizar_lista_record()
        guardar_datos()
        verificar_alertas()
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
        campo_inv = ft.TextField(value=str(inventario.get(nombre, 0)), width=55, height=40, content_padding=5, on_change=actualizar_inventario_desde_inputs, text_align="center")
        inputs_inventario[nombre] = campo_inv
        btn = ft.ElevatedButton(content=ft.Text(nombre, size=11, weight="bold", color="white", text_align="center"), on_click=seleccionar_boton, bgcolor="green", width=132, height=40)
        botones_lista.append(btn)
        return ft.Row([campo_inv, btn], alignment="center")

    def limpiar_historial_cortes(e):
        global historial_cortes
        historial_cortes.clear()
        guardar_datos()
        cambiar_pantalla("historial")

    def eliminar_corte(corte):
        global historial_cortes
        if corte in historial_cortes:
            historial_cortes.remove(corte)
            guardar_datos()
            cambiar_pantalla("historial")

    def cambiar_pantalla(destino):
        page.controls.clear()
        header = ft.Container(content=ft.Text("Pan Casero PATTY", size=20, weight="bold", color="white", text_align="center"), bgcolor="#D84315", padding=10, width=float('inf'))
        page.add(header)
        
        if destino == "sistema":
            iniciar_sistema(False)
        elif destino == "historial":
            elementos = []
            for c in historial_cortes:
                reinversion = c.get('reinversion', c['total'] * 0.50)
                ganancia = c.get('ganancia', c['total'] * 0.50)
                
                btn_borrar_individual = ft.ElevatedButton(
                    "X", 
                    on_click=lambda e, cort=c: eliminar_corte(cort), 
                    bgcolor="red", 
                    color="white", 
                    height=35, 
                    width=45
                )

                card = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(f"📅 Fecha: {c['fecha']}", size=15, weight="bold", color="black"),
                            ft.Text(f" Total Corte: ${c['total']:.2f}", size=14, weight="bold", color="black"),
                            ft.Text(f" 🔵 Reinversión (50%): ${reinversion:.2f}", size=13, color="blue"),
                            ft.Text(f" 🟢 Ganancia (50%): ${ganancia:.2f}", size=13, color="green"),
                        ], expand=True),
                        btn_borrar_individual
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    margin=5,
                    border_radius=8,
                    bgcolor="white",
                    width=320
                )
                elementos.append(card)

            lista_elementos_historial = ft.Column(elementos, horizontal_alignment=ft.CrossAxisAlignment.CENTER) if elementos else ft.Text("No hay cortes guardados aún.", size=14)
            
            page.add(ft.Container(content=ft.Column([
                ft.Text("Historial de Cortes Guardados", size=18, weight="bold"),
                lista_elementos_historial,
                ft.Container(height=10),
                ft.ElevatedButton("BORRAR TODO EL HISTORIAL", on_click=limpiar_historial_cortes, bgcolor="red", color="white"),
                ft.ElevatedButton("VOLVER A OPCIONES", on_click=lambda e: cambiar_pantalla("opciones")),
                ft.Container(height=20)
            ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER), bgcolor="#F1C40F", padding=10))
        else:
            cincuenta_por_ciento = suma_total_dinero * 0.50
            page.add(ft.Container(content=ft.Column([
                ft.Text(f"Total Vendido Hoy: ${suma_total_dinero:.2f}", size=20, weight="bold", color="black"), 
                ft.Text(f"50% Reinversión: ${cincuenta_por_ciento:.2f}", size=20, weight="bold", color="blue"), 
                ft.Text(f"50% Ganancia Total: ${cincuenta_por_ciento:.2f}", size=20, weight="bold", color="green"), 
                ft.ElevatedButton("VER HISTORIAL DE CORTES", on_click=lambda e: cambiar_pantalla("historial"), bgcolor="purple", color="white"),
                ft.ElevatedButton("VOLVER AL SISTEMA", on_click=lambda e: cambiar_pantalla("sistema"))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), bgcolor="#F1C40F", expand=True))
        page.update()

    def iniciar_sistema(es_login=True):
        if es_login:
            with open(ARCHIVO_SESION, "w") as f: f.write("sesion_iniciada")
        cargar_datos() 
        seccion_izq.controls.clear()
        seccion_izq.controls.extend([crear_bloque(p) for p in precios.keys()] + [lista_visual, resultado_total, pago_recibido, contenedor_teclado, resultado_cambio, ft.ElevatedButton("CONFIRMAR", on_click=confirmar_venta_click, bgcolor="green"), ft.ElevatedButton("CORTE", on_click=realizar_corte_click, bgcolor="blue"), lista_record, total_general_visual, ft.ElevatedButton("ADMINISTRACIÓN", on_click=lambda e: cambiar_pantalla("opciones"), bgcolor="grey", color="white")])
        page.controls.clear()
        header = ft.Container(content=ft.Text("Pan Casero PATTY", size=20, weight="bold", color="white", text_align="center"), bgcolor="#D84315", padding=10, width=float('inf'))
        page.add(header, ft.Row([seccion_izq, seccion_der], expand=True, vertical_alignment=ft.CrossAxisAlignment.START))
        actualizar_lista_record(); verificar_alertas(); page.update()

    if os.path.exists(ARCHIVO_SESION):
        iniciar_sistema(False)
    else:
        campo_clave = ft.TextField(label="Clave", password=True, width=200)
        page.add(ft.Column([campo_clave, ft.ElevatedButton("ENTRAR", on_click=lambda e: iniciar_sistema() if campo_clave.value == "PATTY2026" else None)], alignment="center"))

ft.app(target=main)
