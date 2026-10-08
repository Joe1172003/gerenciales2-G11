import csv
import random

paises = ['Guatemala', 'México', 'El Salvador']
nombres = ['Ana', 'Carlos', 'Luis', 'María', 'José', 'Jorge', 'Marta', 'Lucía', 'Pedro', 'Sofía', 'Fernando', 'Laura', 'Diego', 'Carmen', 'Roberto']
apellidos = ['García', 'Rodríguez', 'López', 'Martínez', 'Pérez', 'Gómez', 'Sánchez', 'Díaz', 'Fernández', 'Torres', 'Ramírez', 'Flores', 'Cruz', 'Morales', 'Ortiz']

with open('/home/elian/Descargas/USAC_semestre2_2026/Repos_USAC/gerenciales2-G11/Proyecto1/DIVISION/Persona4/clientes.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Encabezados en inglés técnico para Odoo
    writer.writerow(['id', 'name', 'email', 'phone', 'country_id/id', 'company_type'])
    for i in range(1, 61):
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        email = f"cliente{i}@example.com"
        pais = random.choice(paises)
        if pais == 'Guatemala':
            cid = 'base.gt'
            telefono = f"+502 5555 {i:04d}"
        elif pais == 'México':
            cid = 'base.mx'
            telefono = f"+52 55 5555 {i:04d}"
        else:
            cid = 'base.sv'
            telefono = f"+503 2222 {i:04d}"
        writer.writerow([f'CLI{i:04d}', nombre, email, telefono, cid, 'person'])
