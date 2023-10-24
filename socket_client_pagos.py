import socket
import tkinter as tk
from tkinter import ttk
import datetime

def display_cuotas_pendientes(cuotas_pendientes):
    tree.delete(*tree.get_children())
    for cuota in cuotas_pendientes:
        tree.insert("", "end", values=cuota)
    app.update_idletasks()

def clear_output_labels():
    output_label.config(text="")
    respuesta_label.config(text="")

def send_action(action):
    host = socket.gethostname()
    port = 5000

    client_socket = socket.socket()

    try:
        client_socket.connect((host, port))
    except socket.error as connect_error:
        output_label.config(text=f"Error al conectar con el servidor: {connect_error}", wraplength=350)
        return

    client_socket.send(action.encode())

    if action == "C":
        client_code = client_socket.recv(1024).decode()
        client_code_label.config(text="Códigos de cliente disponibles: " + client_code)

        client_code = input_entry.get().strip()
        if not client_code:
            output_label.config(text="Por favor, seleccione un código de cliente.")
            return
        client_socket.send(client_code.encode())

        cuotas_pendientes_data = client_socket.recv(1024).decode()
        cuotas_pendientes = eval(cuotas_pendientes_data)
        display_cuotas_pendientes(cuotas_pendientes)
    elif action == "P":
        client_code = client_socket.recv(1024).decode()
        client_code_label.config(text="Códigos de cliente disponibles: " + client_code)

        selected_client_code = input_entry.get().strip()
        if not selected_client_code:
            output_label.config(text="Por favor, seleccione un código de cliente.")
            return

        client_socket.send(selected_client_code.encode())
        respuesta = client_socket.recv(1024).decode()
        respuesta_label.config(text=respuesta)
    elif action == "R":
        client_code = client_socket.recv(1024).decode()
        client_code_label.config(text="Códigos de cliente disponibles: " + client_code)

        selected_client_code = input_entry.get().strip()
        if not selected_client_code:
            output_label.config(text="Por favor, seleccione un código de cliente.")
            return

        client_socket.send(selected_client_code.encode())
        respuesta = client_socket.recv(1024).decode()

        if respuesta == "00":
            output_label.config(text="Reversión exitosa.")
        elif respuesta == "01":
            output_label.config(text="La reversión falló.")
    app.after(5000, clear_output_labels)
    client_socket.close()

app = tk.Tk()
app.title("Cliente Program")
app.geometry("550x500")

main_frame = tk.Frame(app)
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

custom_font = ("Helvetica", 14, "bold")

action_label = tk.Label(main_frame, text="Seleccione una acción (C/P)", font=custom_font)
action_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

client_code_label = tk.Label(main_frame, text="")
client_code_label.grid(row=1, column=0, columnspan=3, pady=5)

input_label = tk.Label(main_frame, text="Ingrese un código de cliente:")
input_label.grid(row=2, column=0, columnspan=3, pady=5)

input_entry = tk.Entry(main_frame)
input_entry.grid(row=3, column=0, columnspan=3, pady=5)

button_frame = tk.Frame(main_frame)
button_frame.grid(row=4, column=0, columnspan=3, pady=10)

action_button_C = tk.Button(button_frame, text="Consulta", command=lambda: send_action("C"))
action_button_C.grid(row=0, column=0, padx=5)

action_button_P = tk.Button(button_frame, text="Pago", command=lambda: send_action("P"))
action_button_P.grid(row=0, column=1, padx=5)

action_button_R = tk.Button(button_frame, text="Reversión", command=lambda: send_action("R"))
action_button_R.grid(row=0, column=2, padx=5)

tree = ttk.Treeview(main_frame, columns=("Cuotas", "Monto", "Fecha de Pago"))
tree.heading("#0", text="Cuota", anchor="center")
tree.heading("#1", text="Monto", anchor="center")
tree.heading("#2", text="Fecha de Pago", anchor="center")
tree.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

tree.column("#0", width=50, anchor="w")
tree.column("#1", width=100, anchor="w")
tree.column("#2", width=150, anchor="w")

output_label = tk.Label(main_frame, text="")
output_label.grid(row=6, column=0, columnspan=3, pady=5)

respuesta_label = tk.Label(main_frame, text="")
respuesta_label.grid(row=6, column=0, columnspan=3, pady=5)

app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

app.configure(bg="gray")

app.mainloop()

