import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Sistema PATTY - Control Total"
    page.theme_mode = "light"
    page.bgcolor = "#E0E0E0"
    page.scroll = "adaptive"
    
    inventario = {'Concha': 0, 'Frances lagunero': 0, 'Concha nuez': 0, 'Galleta chispas choc': 0}
    precios = {'Concha': 14.0, 'Frances lagunero': 10.0, 'Concha nuez': 17.0, 'Galleta chispas choc': 10.0}
    
    ventas_totales_cantidad = {producto: 0 for producto in precios}
    ventas_totales_dinero = {producto: 0.0 for producto in precios}
    suma_total_dinero = 0.0
    numero_ventas = 0 
    
    carrito = []
    pan_activo = {"nombre": None}

    lista_visual = ft.ListView(height=80)
    lista_record = ft.ListView(height=120) # RECUPERADO: El detalle por producto
    resultado_total = ft.Text(value="Total a pagar: $0.00", size=20, weight="bold", color="black")
    resultado_cambio = ft.Text(value="Cambio: $0.00", size=20, weight="bold", color="green")
    pago_recibido = ft.TextField(label="Efectivo Recibido ($)", keyboard_type="number", color="black")
    cantidad = ft.TextField(label="Cantidad", keyboard_type="number", color="black")
    
    ventas_realizadas_visual = ft.Text(value="Ventas realizadas: 0", size=18, weight="bold", color="black")
    total_general_visual = ft.Text(value="TOTAL VENDIDO HOY: $0.00", size=24, weight="bold", color="#D4AF37")

    inputs_inventario = {}

    def actualizar_inventario_desde_inputs(e):
        for pan, input_field in inputs_inventario.items():
            if input_field.value and input_field.value.isdigit():
                inventario[pan] = int(input_field.value)
        page.update()

    contenedor_productos = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER)
    botones_lista = []
    
    def seleccionar_boton(e):
        for b in botones_lista: b.bgcolor = "white"
        e.control.bgcolor = "green"
        pan_activo["nombre"] = e.control.content.value
        page.update()

    for nombre in precios.keys():
        campo_inv = ft.TextField(
            hint_text="Inv.", width=70, height=40, text_size=12, 
            keyboard_type="number", on_change=actualizar_inventario_desde_inputs
        )
        inputs_inventario[nombre] = campo_inv
        btn = ft.ElevatedButton(
            content=ft.Text(nombre, size=12, color="black"), 
            on_click=seleccionar_boton, bgcolor="white",
            style=ft.ButtonStyle(padding=5)
        )
        botones_lista.append(btn)
        contenedor_productos.controls.append(ft.Column([campo_inv, btn], alignment=ft.MainAxisAlignment.CENTER, spacing=0))

    def agregar_click(e):
        pan = pan_activo["nombre"]
        cant_str = cantidad.value
        if pan and cant_str.isdigit():
            cant = int(cant_str)
            if inventario[pan] >= cant:
                carrito.append({'pan': pan, 'cant': cant, 'subtotal': precios[pan] * cant})
                lista_visual.controls.append(ft.Text(f"{pan} x{cant} = ${precios[pan]*cant:.2f}", color="black"))
                total_final = sum(item['subtotal'] for item in carrito)
                resultado_total.value = f"Total a pagar: ${total_final:.2f}"
                cantidad.value = ""
            else:
                page.dialog = ft.AlertDialog(title=ft.Text(f"¡Solo quedan {inventario[pan]} pzas de {pan}!"))
                page.dialog.open = True
            page.update()

    def confirmar_venta_click(e):
        nonlocal suma_total_dinero, numero_ventas
        if not carrito: return
        
        numero_ventas += 1
        ventas_realizadas_visual.value = f"Ventas realizadas: {numero_ventas}"
        
        for item in carrito:
            inventario[item['pan']] -= item['cant']
            ventas_totales_cantidad[item['pan']] += item['cant']
            ventas_totales_dinero[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
            inputs_inventario[item['pan']].value = str(inventario[item['pan']])
        
        # Actualizamos la lista de récord (el detalle de productos)
        lista_record.controls.clear()
        for pan in precios:
            if ventas_totales_cantidad[pan] > 0:
                lista_record.controls.append(ft.Text(f"{pan}: {ventas_totales_cantidad[pan]} pzas | ${ventas_totales_dinero[pan]:.2f}", color="black"))
        
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        carrito.clear()
        lista_visual.controls.clear()
        resultado_total.value = "Total: $0.00"
        resultado_cambio.value = "Cambio: $0.00"
        pago_recibido.value = ""
        cantidad.value = ""
        pan_activo["nombre"] = None
        for b in botones_lista: b.bgcolor = "white"
        page.update()

    def realizar_corte_click(e):
        nonlocal suma_total_dinero, numero_ventas
        ruta_archivo = "corte_caja_patty.txt"
        try:
            texto_reporte = f"\n--- CORTE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
            texto_reporte += f"Ventas realizadas: {numero_ventas}\n"
            for pan in precios:
                if ventas_totales_cantidad[pan] > 0:
                    texto_reporte += f"{pan}: {ventas_totales_cantidad[pan]} pzas - ${ventas_totales_dinero[pan]:.2f}\n"
            texto_reporte += f"TOTAL: ${suma_total_dinero:.2f}\n------------------------------\n"
            
            with open(ruta_archivo, "a", encoding="utf-8") as f:
                f.write(texto_reporte)
            
            suma_total_dinero = 0.0
            numero_ventas = 0
            for pan in precios:
                ventas_totales_cantidad[pan] = 0
                ventas_totales_dinero[pan] = 0.0
            
            ventas_realizadas_visual.value = "Ventas realizadas: 0"
            total_general_visual.value = "TOTAL VENDIDO HOY: $0.00"
            lista_record.controls.clear()
            page.dialog = ft.AlertDialog(title=ft.Text("¡Corte guardado con éxito!"))
        except Exception as err:
            page.dialog = ft.AlertDialog(title=ft.Text(f"Error: {str(err)}"))
        page.dialog.open = True
        page.update()

    pago_recibido.on_change = lambda e: (lambda v: (setattr(resultado_cambio, 'value', f"Cambio: ${float(v)-sum(i['subtotal'] for i in carrito):.2f}" if float(v)>=sum(i['subtotal'] for i in carrito) else f"Faltan: ${abs(float(v)-sum(i['subtotal'] for i in carrito)):.2f}"), setattr(resultado_cambio, 'color', "green" if float(v)>=sum(i['subtotal'] for i in carrito) else "red")))(pago_recibido.value) if pago_recibido.value else None

    page.add(
        ft.Container(
            content=ft.Text("Pan Casero PATTY", size=30, weight="bold", color="orange"),
            padding=10
        ),
        contenedor_productos,
        cantidad,
        ft.ElevatedButton("AGREGAR AL CARRITO", on_click=agregar_click, bgcolor="orange"),
        lista_visual, resultado_total,
        pago_recibido, resultado_cambio,
        ft.ElevatedButton("CONFIRMAR VENTA", on_click=confirmar_venta_click, bgcolor="green"),
        ft.ElevatedButton("REALIZAR CORTE", on_click=realizar_corte_click, bgcolor="blue"),
        ft.Divider(),
        ventas_realizadas_visual,
        lista_record, 
        total_general_visual
    )

ft.app(target=main)
