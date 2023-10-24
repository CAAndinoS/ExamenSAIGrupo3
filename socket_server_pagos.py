import socket
import mysql.connector

# Definimos una función llamada 'server_program'
def server_program():
    try:
        # Obtenemos el nombre del host local
        host = socket.gethostname()
        # Especificamos el número de puerto en el que el servidor escuchará
        port = 5000

        # Crear una conexión a la base de datos MySQL
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sa1"
        )

        cursor = db_connection.cursor()

        # Creamos un socket del servidor
        server_socket = socket.socket()

        try:
            # Vinculamos el socket del servidor al host y al puerto especificados
            server_socket.bind((host, port))
        except socket.error as bind_error:
            print(f"Error al vincular el servidor al puerto: {bind_error}")
            return  # Salimos de la función si hay un error de vinculación

        # Configuramos cuántos clientes pueden estar en espera de conexión simultáneamente
        server_socket.listen(2)
        print("Servidor esperando conexiones en el puerto", port)

        while True:
            conn, address = server_socket.accept()
            print("Conexión desde: " + str(address))

            try:
                # Iniciamos un bucle infinito para la comunicación con el cliente
                while True:
                    # Recibimos datos del cliente (hasta 1024 bytes) y los decodificamos
                    data = conn.recv(1024).decode()
                    if not data:
                        break

                    # Imprimimos los datos recibidos del cliente en la consola del servidor
                    print("Del usuario conectado: " + str(data))

                    if data == "C":
                        # Realizar una consulta en la base de datos y obtener los códigos de cliente
                        cursor.execute("SELECT DISTINCT id_cliente FROM pagos WHERE estado = 'P'")
                        results = cursor.fetchall()
                        client_codes = [str(result[0]) for result in results]
                        client_codes_str = ', '.join(client_codes)

                        # Enviar los códigos de cliente al cliente
                        conn.send(client_codes_str.encode())

                        # Esperar a que el cliente ingrese un código de cliente
                        data = conn.recv(1024).decode()
                        client_code = data
                        # Realizar una consulta para obtener las cuotas pendientes del cliente
                        cursor.execute(
                            "SELECT cuota, monto, fecha_pago FROM pagos WHERE id_cliente = %s AND estado = 'P'",
                            (client_code,))
                        results = cursor.fetchall()
                        # Enviar los resultados al cliente
                        conn.send(str(results).encode())
                    elif data == "P":
                        # Realizar una consulta en la base de datos y obtener los códigos de cliente
                        cursor.execute("SELECT DISTINCT id_cliente FROM pagos")
                        results = cursor.fetchall()
                        client_codes = [str(result[0]) for result in results]
                        client_codes_str = ', '.join(client_codes)
                        # Enviar los códigos de cliente al cliente
                        conn.send(client_codes_str.encode())
                        # Esperar a que el cliente ingrese un código de cliente
                        data = conn.recv(1024).decode()
                        client_code = data
                        # Obtener la cuota más próxima a pagar para el cliente
                        cursor.execute(
                            "SELECT cuota, monto, fecha_pago FROM pagos WHERE id_cliente = %s AND estado = 'P' ORDER BY fecha_pago LIMIT 1",
                            (client_code,))
                        result = cursor.fetchone()
                        if result:
                            cuota_numero = result[0]
                            # Actualizar el estado de la cuota a 'C', establecer la fecha de pago y la referencia
                            cursor.execute(
                                "UPDATE pagos SET estado = 'C', pago_fecha_realizacion = NOW(), referencia = CONCAT(%s, '_', %s) WHERE id_cliente = %s AND estado = 'P' LIMIT 1",
                                (client_code, cuota_numero, client_code))
                            db_connection.commit()
                            conn.send(f"La cuota {cuota_numero} ha sido pagada exitosamente.".encode())
                        else:
                            conn.send("No hay cuotas pendientes para pagar.".encode())

                    elif data == "R":
                        # Realizar una consulta en la base de datos y obtener los códigos de cliente
                        cursor.execute("SELECT DISTINCT id_cliente FROM pagos")
                        results = cursor.fetchall()
                        client_codes = [str(result[0]) for result in results]
                        client_codes_str = ', '.join(client_codes)
                        # Enviar los códigos de cliente al cliente
                        conn.send(client_codes_str.encode())
                        # Esperar a que el cliente ingrese un código de cliente
                        data = conn.recv(1024).decode()
                        client_code = data

                        # Obtener la última cuota en estado 'C' para el cliente
                        cursor.execute(
                            "SELECT cuota FROM pagos WHERE id_cliente = %s AND estado = 'C' ORDER BY cuota DESC LIMIT 1",
                            (client_code,))
                        last_paid_cuota = cursor.fetchone()

                        if last_paid_cuota:
                            # Realizar la reversión solo para la última cuota en estado 'C'
                            cursor.execute(
                                "UPDATE pagos SET estado = 'P', pago_fecha_realizacion = NULL, referencia = NULL WHERE id_cliente = %s AND cuota = %s",
                                (client_code, last_paid_cuota[0]))
                            db_connection.commit()
                            conn.send("00".encode())  # Código 00 para éxito
                        else:
                            conn.send("01".encode())  # Código 01 para fallo (no hay cuotas para revertir)
                    else:
                        conn.send("Acción no válida.".encode())
            except socket.error as recv_error:
                print(f"Error al recibir datos del cliente: {recv_error}")
                break  # Salimos del bucle si hay un error al recibir datos
            finally:
                # Cerramos la conexión con el cliente
                conn.close()
    except Exception as e:
        print(f"Error inesperado en el servidor: {e}")
    finally:
        # Cerramos la conexión con la base de datos al salir del programa
        cursor.close()
        db_connection.close()
        server_socket.close()

# Iniciamos la función 'server_program' si el archivo se ejecuta directamente
if __name__ == '__main__':
    server_program()