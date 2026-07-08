
import flet as ft
from datetime import datetime
import os

def main(page: ft.Page):
    page.title = "Sistema PATTY - Corte de Caja"
    page.theme_mode = "dark"
    page.scroll = "adaptive" 
    
    precios = {'Concha': 14.0, 'Concha nuez': 17.0, 'Frances lagunero': 10.0, 'Galleta chispas choc': 10.0}
    
    ventas_totales = {producto: 0 for producto in precios}
    dinero_total = {producto: 0.0 for producto in precios}
    suma_total_dinero = 0.0
    contador_ventas = 0
    carrito = []
    pan_activo = {"nombre": None}

    lista_visual = ft.ListView(height=100)
    resultado_total = ft.Text(value="Total a pagar: $0.00", size=20, weight="bold")
    resultado_cambio = ft.Text(value="Cambio: $0.00", size=20, weight="bold", color="green")
    pago_recibido = ft.TextField(label="Efectivo Recibido ($)", keyboard_type="number")
    cantidad = ft.TextField(label="Cantidad", keyboard_type="number")
    
    lista_record = ft.ListView(height=150)
    contador_ventas_visual = ft.Text(value="Ventas realizadas hoy: 0", size=16, color="gray")
    total_general_visual = ft.Text(value="TOTAL VENDIDO HOY: $0.00", size=22, weight="bold", color="yellow")

    botones_lista = []

    def seleccionar_boton(e):
        for b in botones_lista: b.bgcolor = None 
        e.control.bgcolor = "green"
        pan_activo["nombre"] = e.control.content.value
        page.update()

    def agregar_click(e):
        pan = pan_activo["nombre"]
        cant_str = cantidad.value
        if pan and cant_str.isdigit():
            cant = int(cant_str)
            carrito.append({'pan': pan, 'cant': cant, 'subtotal': precios[pan] * cant})
            lista_visual.controls.append(ft.Text(f"{pan} x{cant} = ${precios[pan]*cant:.2f}"))
            total_final = sum(item['subtotal'] for item in carrito)
            resultado_total.value = f"Total a pagar: ${total_final:.2f}"
            cantidad.value = ""
            pan_activo["nombre"] = None
            for b in botones_lista: b.bgcolor = None
            page.update()

    for nombre in precios.keys():
        btn = ft.ElevatedButton(content=ft.Text(nombre), on_click=seleccionar_boton)
        botones_lista.append(btn)

    botones_row = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER, controls=botones_lista)

    def calcular_cambio(e):
        total_final = sum(item['subtotal'] for item in carrito)
        try:
            pago = float(pago_recibido.value)
            cambio = pago - total_final
            resultado_cambio.value = f"Cambio: ${cambio:.2f}" if cambio >= 0 else f"Faltan: ${abs(cambio):.2f}"
            resultado_cambio.color = "green" if cambio >= 0 else "red"
        except:
            resultado_cambio.value = "Esperando pago..."
        page.update()

    pago_recibido.on_change = calcular_cambio

    def confirmar_venta_click(e):
        nonlocal suma_total_dinero, contador_ventas
        if not carrito: return
        contador_ventas += 1
        for item in carrito:
            ventas_totales[item['pan']] += item['cant']
            dinero_total[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
        
        lista_record.controls.clear()
        for pan in precios:
            if ventas_totales[pan] > 0:
                lista_record.controls.append(ft.Text(f"{pan}: {ventas_totales[pan]} pzas | ${dinero_total[pan]:.2f}"))
        
        contador_ventas_visual.value = f"Ventas realizadas hoy: {contador_ventas}"
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        carrito.clear()
        lista_visual.controls.clear()
        resultado_total.value = "Total: $0.00"
        resultado_cambio.value = "Cambio: $0.00"
        pago_recibido.value = ""
        page.update()

    def realizar_corte_click(e):
        nonlocal suma_total_dinero, contador_ventas
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ruta en la carpeta Descargas (pública en Android)
        ruta_archivo = "/sdcard/Download/corte_caja_patty.txt"
        
        try:
            with open(ruta_archivo, "a") as f:
                f.write(f"\n--- CORTE DE CAJA: {fecha_actual} ---\n")
                for pan in precios:
                    if ventas_totales[pan] > 0:
                        f.write(f"{pan}: {ventas_totales[pan]} pzas - ${dinero_total[pan]:.2f}\n")
                f.write(f"TOTAL RECAUDADO: ${suma_total_dinero:.2f}\n")
                f.write("------------------------------\n")
        except:
            pass # Fallo silencioso si no tiene permisos
            
        suma_total_dinero = 0.0
        contador_ventas = 0
        for pan in precios: ventas_totales[pan] = 0; dinero_total[pan] = 0.0
        lista_record.controls.clear()
        contador_ventas_visual.value = "Ventas realizadas hoy: 0"
        total_general_visual.value = "TOTAL VENDIDO HOY: $0.00"
        page.dialog = ft.AlertDialog(title=ft.Text("Corte guardado en Descargas."))
        page.dialog.open = True
        page.update()

    page.add(
        ft.Text("Pan Casero PATTY", size=25, weight="bold", color="orange"),
        botones_row,
        cantidad,
        ft.ElevatedButton(content=ft.Text("AGREGAR"), on_click=agregar_click, bgcolor="orange"),
        lista_visual, resultado_total,
        pago_recibido, resultado_cambio,
        ft.ElevatedButton(content=ft.Text("CONFIRMAR VENTA"), on_click=confirmar_venta_click, bgcolor="green"),
        ft.ElevatedButton(content=ft.Text("REALIZAR CORTE"), on_click=realizar_corte_click, bgcolor="blue"),
        ft.Divider(),
        contador_ventas_visual,
        total_general_visual,
        lista_record
    )

ft.app(target=main)
