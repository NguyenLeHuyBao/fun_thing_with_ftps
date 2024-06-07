from ftplib import FTP, error_perm
import socket


class FTPManager:
    def __init__(self, host, port, usr, passwd, base_dir):
        self.host = host
        self.port = port
        self.usr = usr
        self.passwd = passwd
        self.base_dir = base_dir

    def _create_connection(self):
        try:
            ftp = FTP()
            ftp.connect(self.host, self.port, timeout=30)
            ftp.login(self.usr, self.passwd)
            ftp.set_pasv(True)
            print(f"Connected to {self.host}:{self.port}")
            print("Directory contents:", ftp.nlst())
            return ftp
        except (socket.timeout, ConnectionRefusedError) as e:
            print(f"Failed to connect to {self.host}:{self.port} - {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def get_connection(self):
        return self._create_connection()
