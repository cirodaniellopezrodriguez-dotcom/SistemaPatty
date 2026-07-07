import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Sistema PATTY - Corte de Caja"
    page.theme_mode = "dark"
    page.scroll = "adaptive" # Esto permite que si el contenido es largo, puedas hacer scroll y no se pierda nada
    
    precios = {'Concha': 14.0, 'Concha nuez': 17.0, 'Frances lagunero': 10.0, 'Galleta chispas choc': 10.0}
    
    ventas_totales = {producto: 0 for producto in precios}
    dinero_total = {producto: 0.0 for producto in precios}
    suma_total_dinero = 0.0
    carrito = []

    # UI
    dropdown = ft.Dropdown(label="Selecciona Pan", options=[ft.dropdown.Option(k) for k in precios.keys()])
    cantidad = ft.TextField(label="Cantidad", keyboard_type="number")
    lista_visual = ft.ListView(height=100)
    resultado_total = ft.Text(value="Total a pagar: $0.00", size=20, weight="bold")
    resultado_cambio = ft.Text(value="Cambio: $0.00", size=20, weight="bold", color="green")
    pago_recibido = ft.TextField(label="Efectivo Recibido ($)", keyboard_type="number")
    
    lista_record = ft.ListView(height=150)
    total_general_visual = ft.Text(value="TOTAL VENDIDO HOY: $0.00", size=22, weight="bold", color="yellow")

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

    def agregar_click(e):
        pan = dropdown.value
        cant = int(cantidad.value) if cantidad.value.isdigit() else 0
        if pan in precios and cant > 0:
            carrito.append({'pan': pan, 'cant': cant, 'subtotal': precios[pan] * cant})
            lista_visual.controls.append(ft.Text(f"{pan} x{cant} = ${precios[pan]*cant:.2f}"))
            total_final = sum(item['subtotal'] for item in carrito)
            resultado_total.value = f"Total a pagar: ${total_final:.2f}"
            cantidad.value = ""
            page.update()

    def realizar_corte_click(e):
        nonlocal suma_total_dinero
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Guardar archivo
        with open("corte_caja_patty.txt", "a") as f:
            f.write(f"\n--- CORTE DE CAJA: {fecha_actual} ---\n")
            for pan in precios:
                if ventas_totales[pan] > 0:
                    f.write(f"{pan}: {ventas_totales[pan]} pzas - ${dinero_total[pan]:.2f}\n")
            f.write(f"TOTAL RECAUDADO: ${suma_total_dinero:.2f}\n")
            f.write("-" * 30 + "\n")
            
        # 2. REINICIO DE VARIABLES (El detalle que faltaba)
        for pan in precios:
            ventas_totales[pan] = 0
            dinero_total[pan] = 0.0
        suma_total_dinero = 0.0
        
        # 3. Limpiar pantalla
        lista_record.controls.clear()
        total_general_visual.value = "TOTAL VENDIDO HOY: $0.00"
        
        page.dialog = ft.AlertDialog(title=ft.Text("Corte realizado con éxito y sistema reiniciado."))
        page.dialog.open = True
        page.update()

    def confirmar_venta_click(e):
        nonlocal suma_total_dinero
        for item in carrito:
            ventas_totales[item['pan']] += item['cant']
            dinero_total[item['pan']] += item['subtotal']
            suma_total_dinero += item['subtotal']
        
        lista_record.controls.clear()
        for pan in precios:
            if ventas_totales[pan] > 0:
                lista_record.controls.append(ft.Text(f"{pan}: {ventas_totales[pan]} pzas | ${dinero_total[pan]:.2f}"))
        
        total_general_visual.value = f"TOTAL VENDIDO HOY: ${suma_total_dinero:.2f}"
        carrito.clear()
        lista_visual.controls.clear()
        resultado_total.value = "Total: $0.00"
        resultado_cambio.value = "Cambio: $0.00"
        pago_recibido.value = ""
        page.update()

    page.add(
        ft.Text("Pan Casero PATTY", size=30, weight="bold", color="orange"),
        dropdown, cantidad,
        ft.ElevatedButton("AGREGAR", on_click=agregar_click),
        lista_visual, resultado_total,
        pago_recibido, resultado_cambio,
        ft.ElevatedButton("CONFIRMAR VENTA", on_click=confirmar_venta_click, bgcolor="green"),
        ft.ElevatedButton("REALIZAR CORTE DE CAJA", on_click=realizar_corte_click, bgcolor="blue"),
        ft.Divider(),
        total_general_visual,
        lista_record
    )

ft.app(target=main)