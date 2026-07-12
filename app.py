import flet as ft
from datetime import datetime
import json
import os

ARCHIVO_DATOS = "datos_patty.json"
ARCHIVO_SESION = "sesion_activa.json"

def main(page: ft.Page):
    page.title = "Sistema PATTY - Control Total"
    page.theme_mode = "light"
    page.bgcolor = "#F1C40F" 
    page.padding = 0

    seccion_izq = ft.Column(width=220)
    seccion_der = ft.Column(expand=True)
    main_layout = ft.Row([seccion_izq, seccion_der], alignment="start", vertical_alignment="start")
    main_content = ft.Column([main_layout], scroll="adaptive", expand=True)

    inventario = {'Concha': 0, 'Frances lagunero': 0, 'Concha nuez': 0, 'Galleta chispas choc': 0}
    precios = {'Concha': 14.0, 'Frances lagunero': 10.0, 'Concha nuez': 17.0, 'Galleta chispas choc': 10.0}
    ventas_totales_cantidad = {producto: 0 for producto in precios}
    ventas_totales_dinero = {producto: 0.0 for producto in precios}
    suma_total_dinero = 0.0
    numero_ventas = 0 
    carrito = []
    pan_activo = {"nombre": None}
    inputs_inventario = {}
    botones_lista = []

    def guardar_datos():
        datos = {"inventario": inventario, "ventas_cantidad": ventas_totales_cantidad, "ventas_dinero": ventas_totales_dinero, "suma_total": suma_total_dinero, "num_ventas": numero_ventas}
        with open(ARCHIVO_DATOS, "w") as f: json.dump(datos, f)

    def cargar_datos():
        nonlocal suma_total_dinero, numero_ventas
        if os.path.exists(ARCHIVO_DATOS):
            with open(ARCHIVO_DATOS, "r") as f:
                datos = json.load(f)
                inventario.update(datos["inventario"])
                ventas_totales_cantidad.update(datos["ventas_cantidad"])
                ventas_totales_dinero.update(datos["ventas_dinero"])
                suma_total_dinero = datos["suma_total"]
                numero_ventas = datos["num_ventas"]

    def verificar_alertas():
        for pan, campo in inputs_inventario.items():
            if inventario[pan] <= 5:
                campo.border_color = "red"
                campo.border_width = 2
            else:
                campo.border_color = None
                campo.border_width = 1
        page.update()

    def actualizar_inventario_desde_inputs(e):
        for pan, input_field in inputs_inventario.items():
            if input_field.value and input_field.value.isdigit():
                inventario[pan] = int(input_field.value)
        guardar_datos()
        verificar_alertas()

    def actualizar_lista_record():
        lista_record.controls.clear()
        for pan in precios:
            if ventas_totales_cantidad[pan] > 0:
                fila_info = ft.Row([
                    ft.Text(f"{pan}:", weight="bold", size=12, color="black"),
                    ft.Text(f"{ventas_totales_cantidad[pan]} pzas | ${ventas_totales_dinero[pan]:.2f}", size=12, color="black")
                ], alignment="start", spacing=5)
                lista_record.controls.append(fila_info)
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        page.update()

    def seleccionar_boton(e):
        for b in botones_lista: 
            b.bgcolor = "green"
            b.content.color = "white"
        e.control.bgcolor = "yellow"
        e.control.content.color = "black"
        pan_activo["nombre"] = e.control.content.value
        seccion_der.controls.clear()
        for i in range(1, 11):
            btn = ft.ElevatedButton(str(i), on_click=lambda e, n=i: procesar_seleccion(n), width=50, height=30)
            seccion_der.controls.append(btn)
        page.update()

    def procesar_seleccion(n):
        pan = pan_activo["nombre"]
        if pan and inventario[pan] >= n:
            producto = {'pan': pan, 'cant': n, 'subtotal': precios[pan] * n}
            carrito.append(producto)
            def eliminar_item(e, item=producto):
                carrito.remove(item); lista_visual.controls.remove(fila_item)
                resultado_total.value = f"Total: ${sum(i['subtotal'] for i in carrito):.2f}"
                page.update()
            fila_item = ft.Row([ft.ElevatedButton("X", on_click=eliminar_item, bgcolor="red", color="white", height=30), ft.Text(f"{pan} x{n} = ${precios[pan]*n:.2f}", size=12, color="black")])
            lista_visual.controls.append(fila_item)
            resultado_total.value = f"Total: ${sum(i['subtotal'] for i in carrito):.2f}"
            seccion_der.controls.clear()
            for b in botones_lista: 
                b.bgcolor = "green"
                b.content.color = "white"
            page.update()

    def mostrar_teclado(e):
        contenedor_teclado.visible = True
        page.update()

    # --- Teclado con colores personalizados ---
    def teclado_presionada(e):
        valor = e.control.content.value
        if valor == "C": pago_recibido.value = ""
        elif valor == "OK": contenedor_teclado.visible = False
        else: pago_recibido.value += str(valor)
        calcular_cambio()
        page.update()

    def crear_boton_t(val):
        color_fondo = "white"
        if val == "C": color_fondo = "red"
        elif val == "OK": color_fondo = "green"
        
        return ft.ElevatedButton(
            content=ft.Text(val, color="white" if color_fondo != "white" else "black"), 
            on_click=teclado_presionada, 
            width=50, 
            bgcolor=color_fondo
        )

    contenedor_teclado = ft.Container(content=ft.Column([
        ft.Row([crear_boton_t("1"), crear_boton_t("2"), crear_boton_t("3")]),
        ft.Row([crear_boton_t("4"), crear_boton_t("5"), crear_boton_t("6")]),
        ft.Row([crear_boton_t("7"), crear_boton_t("8"), crear_boton_t("9")]),
        ft.Row([crear_boton_t("0"), crear_boton_t("C"), crear_boton_t("OK")])
    ]), visible=False, padding=5, bgcolor="white")

    def confirmar_venta_click(e):
        nonlocal suma_total_dinero, numero_ventas
        if not carrito: return
        numero_ventas += 1
        for item in carrito:
            inventario[item['pan']] -= item['cant']
            ventas_totales_cantidad[item['pan']] += item['cant']
            ventas_totales_dinero[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
            inputs_inventario[item['pan']].value = str(inventario[item['pan']])
        carrito.clear(); lista_visual.controls.clear(); resultado_total.value = "Total: $0.00"
        pago_recibido.value = ""; resultado_cambio.value = "Cambio: $0.00"
        contenedor_teclado.visible = False
        actualizar_lista_record(); guardar_datos(); verificar_alertas(); page.update()

    def realizar_corte_click(e):
        nonlocal suma_total_dinero, numero_ventas
        suma_total_dinero, numero_ventas = 0.0, 0
        for pan in precios: ventas_totales_cantidad[pan], ventas_totales_dinero[pan] = 0, 0.0
        actualizar_lista_record(); guardar_datos(); verificar_alertas(); page.update()

    def calcular_cambio(e=None):
        total = sum(i['subtotal'] for i in carrito)
        try:
            pago = float(pago_recibido.value)
            diff = pago - total
            resultado_cambio.value = f"Cambio: ${diff:.2f}" if diff >= 0 else f"Faltan: ${abs(diff):.2f}"
            resultado_cambio.color = "green" if diff >= 0 else "red"
        except: resultado_cambio.value = "Cambio: $0.00"
        page.update()

    lista_visual = ft.Column()
    lista_record = ft.Column()
    resultado_total = ft.Text("Total: $0.00", size=18, weight="bold", color="black")
    resultado_cambio = ft.Text("Cambio: $0.00", size=18, weight="bold", color="black")
    pago_recibido = ft.TextField(label="Efectivo Recibido ($)", width=180, read_only=True, on_focus=mostrar_teclado)
    total_general_visual = ft.Text(value="TOTAL VENDIDO HOY: $0.00", size=16, weight="bold", color="black")
    
    def crear_bloque(nombre):
        campo_inv = ft.TextField(value=str(inventario.get(nombre, 0)), width=50, height=40, content_padding=5, keyboard_type="number", on_change=actualizar_inventario_desde_inputs)
        inputs_inventario[nombre] = campo_inv
        btn = ft.ElevatedButton(content=ft.Text(nombre, size=11, weight="bold", color="white"), on_click=seleccionar_boton, bgcolor="green", width=120, height=40)
        botones_lista.append(btn)
        return ft.Row([campo_inv, btn], alignment="start", spacing=5)

    def iniciar_sistema(es_login=True):
        if es_login:
            with open(ARCHIVO_SESION, "w") as f: f.write("sesion_iniciada")
        
        page.controls.clear()
        header = ft.Container(content=ft.Text("Pan Casero PATTY", size=20, weight="bold", color="white", text_align="center"), bgcolor="#D84315", padding=10, width=float('inf'))
        cargar_datos()
        seccion_izq.controls.clear()
        seccion_izq.controls.extend([crear_bloque(p) for p in precios.keys()])
        seccion_izq.controls.extend([lista_visual, resultado_total, pago_recibido, contenedor_teclado, resultado_cambio, 
                                     ft.ElevatedButton("CONFIRMAR", on_click=confirmar_venta_click, bgcolor="green"),
                                     ft.ElevatedButton("CORTE", on_click=realizar_corte_click, bgcolor="blue"),
                                     lista_record, total_general_visual])
        page.add(header, main_content)
        actualizar_lista_record()
        verificar_alertas()
        page.update()

    if os.path.exists(ARCHIVO_SESION):
        iniciar_sistema(es_login=False)
    else:
        campo_clave = ft.TextField(label="Clave", password=True, width=200)
        page.add(ft.Column([campo_clave, ft.ElevatedButton("ENTRAR", on_click=lambda e: iniciar_sistema() if campo_clave.value == "PATTY2026" else None)], alignment="center"))

ft.app(target=main)
