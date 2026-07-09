
import flet as ft
from datetime import datetime
import json
import os

# Archivos de control
ARCHIVO_DATOS = "datos_patty.json"
ARCHIVO_SESION = "sesion_activa.json" # Este archivo mantiene la app abierta

def main(page: ft.Page):
    page.title = "Sistema PATTY - Control Total"
    page.theme_mode = "light"
    page.bgcolor = "#E0E0E0"
    page.scroll = "adaptive"
    
    # Variables de estado
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

    # --- FUNCIONES DE CONTROL ---
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

    def actualizar_lista_record():
        lista_record.controls.clear()
        for pan in precios:
            if ventas_totales_cantidad[pan] > 0:
                lista_record.controls.append(ft.Text(f"{pan}: {ventas_totales_cantidad[pan]} pzas | ${ventas_totales_dinero[pan]:.2f}", color="black"))
        page.update()

    # --- LÓGICA DE VENTAS ---
    def actualizar_inventario_desde_inputs(e):
        for pan, input_field in inputs_inventario.items():
            if input_field.value and input_field.value.isdigit():
                inventario[pan] = int(input_field.value)
        guardar_datos()

    def seleccionar_boton(e):
        for b in botones_lista: b.bgcolor = "white"
        e.control.bgcolor = "green"
        pan_activo["nombre"] = e.control.content.value
        page.update()

    def agregar_click(e):
        actualizar_inventario_desde_inputs(None)
        pan = pan_activo["nombre"]
        
        if pan and cantidad.value.isdigit():
            cant = int(cantidad.value)
            
            if inventario[pan] >= cant:
                # Creamos el diccionario del producto
                producto = {'pan': pan, 'cant': cant, 'subtotal': precios[pan] * cant}
                carrito.append(producto)
                
                # Función para eliminar este item
                def eliminar_item(e, item=producto):
                    if item in carrito:
                        carrito.remove(item)
                        lista_visual.controls.remove(fila_item)
                        total_actual = sum(i['subtotal'] for i in carrito)
                        resultado_total.value = f"Total a pagar: ${total_actual:.2f}"
                        page.update()

                # Solución final: usamos el botón que tu sistema YA conoce
                fila_item = ft.Row([
                    ft.ElevatedButton(
                        "X", 
                        on_click=eliminar_item,
                        bgcolor="red",
                        color="white"
                    ),
                    ft.Text(f"{pan} x{cant} = ${precios[pan]*cant:.2f}", color="black")
                ])
                
                lista_visual.controls.append(fila_item)
                
                # Recalculamos el total
                total_actual = sum(item['subtotal'] for item in carrito)
                resultado_total.value = f"Total a pagar: ${total_actual:.2f}"
                cantidad.value = ""
                
            else:
                # Si no hay suficiente inventario
                page.dialog = ft.AlertDialog(title=ft.Text(f"¡Solo quedan {inventario[pan]} pzas!"))
                page.dialog.open = True
            
            page.update()

    def confirmar_venta_click(e):
        nonlocal suma_total_dinero, numero_ventas
        
        # 1. Validación de carrito vacío
        if not carrito: 
            return

        # 2. Candado de seguridad: Validar que el pago sea suficiente
        total_a_pagar = sum(item['subtotal'] for item in carrito)
        
        # Si el campo está vacío o el pago es menor al total, bloqueamos la venta
        if not pago_recibido.value or float(pago_recibido.value) < total_a_pagar:
            page.dialog = ft.AlertDialog(
                title=ft.Text("¡Error de pago!"),
                content=ft.Text(f"Debes ingresar un monto igual o mayor a ${total_a_pagar:.2f}")
            )
            page.dialog.open = True
            page.update()
            return # Detenemos la función aquí

        # 3. Si todo es correcto, procesamos la venta
        numero_ventas += 1
        for item in carrito:
            inventario[item['pan']] -= item['cant']
            ventas_totales_cantidad[item['pan']] += item['cant']
            ventas_totales_dinero[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
            inputs_inventario[item['pan']].value = str(inventario[item['pan']])
        
        # 4. Limpieza de pantalla y preparación para siguiente venta
        ventas_realizadas_visual.value = f"Ventas realizadas: {numero_ventas}"
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        carrito.clear()
        lista_visual.controls.clear()
        resultado_total.value = "Total: $0.00"
        resultado_cambio.value = "Cambio: $0.00"
        pago_recibido.value = ""
        pan_activo["nombre"] = None
        for b in botones_lista: b.bgcolor = "white"
        
        actualizar_lista_record()
        guardar_datos()
        page.update()

    def realizar_corte_click(e):
        nonlocal suma_total_dinero, numero_ventas
        with open("corte_caja_patty.txt", "a", encoding="utf-8") as f: 
            f.write(f"\n--- CORTE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\nTOTAL: ${suma_total_dinero:.2f}\n")
        suma_total_dinero, numero_ventas = 0.0, 0
        for pan in precios: ventas_totales_cantidad[pan], ventas_totales_dinero[pan] = 0, 0.0
        ventas_realizadas_visual.value = "Ventas realizadas: 0"
        total_general_visual.value = "TOTAL VENDIDO HOY: $0.00"
        actualizar_lista_record()
        guardar_datos()
        page.update()

    def calcular_cambio(e):
        total_a_pagar = sum(item['subtotal'] for item in carrito)
        if pago_recibido.value and pago_recibido.value.replace('.', '', 1).replace(',', '').isdigit():
            try:
                pago = float(pago_recibido.value)
                diferencia = pago - total_a_pagar
                if diferencia >= 0:
                    resultado_cambio.value = f"Cambio: ${diferencia:.2f}"
                    resultado_cambio.color = "green"
                else:
                    resultado_cambio.value = f"Faltan: ${abs(diferencia):.2f}"
                    resultado_cambio.color = "red"
            except ValueError:
                resultado_cambio.value = "Cambio: $0.00"
        else:
            resultado_cambio.value = "Cambio: $0.00"
            resultado_cambio.color = "green"
        page.update()

    # --- UI Y CONTROL ---
    lista_visual = ft.ListView(height=80)
    lista_record = ft.ListView(height=120)
    resultado_total = ft.Text(value="Total a pagar: $0.00", size=20, weight="bold", color="black")
    resultado_cambio = ft.Text(value="Cambio: $0.00", size=20, weight="bold", color="green")
    pago_recibido = ft.TextField(label="Efectivo Recibido ($)", keyboard_type="number", color="black", on_change=calcular_cambio)
    cantidad = ft.TextField(label="Cantidad", keyboard_type="number", color="black")
    ventas_realizadas_visual = ft.Text(value="Ventas realizadas: 0", size=18, weight="bold", color="black")
    total_general_visual = ft.Text(value="TOTAL VENDIDO HOY: $0.00", size=24, weight="bold", color="#D4AF37")

    def verificar_clave(e):
        if campo_clave.value == "PATTY2026":
            with open(ARCHIVO_SESION, "w") as f: json.dump({"activa": True}, f)
            iniciar_sistema()
        else:
            campo_clave.error_text = "Clave incorrecta"
            page.update()

    def crear_bloque(nombre):
        # Mantenemos el campo de inventario
        campo_inv = ft.TextField(hint_text="Inv.", width=70, height=40, text_size=12, keyboard_type="number", on_change=actualizar_inventario_desde_inputs)
        campo_inv.value = str(inventario.get(nombre, 0))
        inputs_inventario[nombre] = campo_inv
        
        # AQUÍ ESTÁ EL CAMBIO: Fijamos el ancho (width) y alto (height)
        btn = ft.ElevatedButton(
            content=ft.Text(
                nombre, 
                size=16,            # Aumentamos a 16 para que resalte
                weight="bold",      # Negritas para mayor legibilidad
                color="black", 
                text_align="center"
            ), 
            on_click=seleccionar_boton, 
            bgcolor="white", 
            style=ft.ButtonStyle(
                padding=5,
                shape=ft.RoundedRectangleBorder(radius=8) # Bordes un poquito más suaves
            ),
            width=150,  # El ancho que ya definimos
            height=60   # La altura que ya definimos
        )

        botones_lista.append(btn)
        return ft.Column([campo_inv, btn], alignment=ft.MainAxisAlignment.CENTER, spacing=0)

    def dibujar_interfaz():
        prods = list(precios.keys())
        page.controls.clear()
        page.add(
            ft.Text("Pan Casero PATTY", size=24, weight="bold", color="orange"),
            ft.Row([crear_bloque(prods[0]), crear_bloque(prods[1])], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([crear_bloque(prods[2]), crear_bloque(prods[3])], alignment=ft.MainAxisAlignment.CENTER),
            cantidad, 
            ft.ElevatedButton("AGREGAR AL CARRITO", on_click=agregar_click, bgcolor="orange"),
            lista_visual, 
            resultado_total, 
            pago_recibido, 
            resultado_cambio,
            ft.ElevatedButton("CONFIRMAR VENTA", on_click=confirmar_venta_click, bgcolor="green"),
            ft.ElevatedButton("REALIZAR CORTE", on_click=realizar_corte_click, bgcolor="blue"),
            ft.Divider(), 
            ventas_realizadas_visual, 
            lista_record, 
            total_general_visual
        )
        page.update()

    def iniciar_sistema():
        cargar_datos()
        dibujar_interfaz()
        actualizar_lista_record()
        ventas_realizadas_visual.value = f"Ventas realizadas: {numero_ventas}"
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        page.update()

    # --- INICIO ---
    if os.path.exists(ARCHIVO_SESION):
        iniciar_sistema()
    else:
        campo_clave = ft.TextField(label="Clave de Acceso", password=True)
        page.add(ft.Column([ft.Text("ACCESO PATTY", size=20), campo_clave, ft.ElevatedButton("ENTRAR", on_click=verificar_clave)], alignment=ft.MainAxisAlignment.CENTER))

ft.app(target=main)
