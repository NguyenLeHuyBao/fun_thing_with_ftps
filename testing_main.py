from ftplib import FTP, error_perm
import os
import socket
from datetime import datetime, timedelta


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


def rename_deleted(ftp, path):
    prefix = 'deleted_'
    parent_dir, name = os.path.split(path)
    if not name.startswith(prefix):
        new_name = os.path.join(parent_dir, f"{prefix}{name}")
        ftp.rename(path, new_name)
        print(f"Renamed {path} to {new_name}")


def create_remote_dir(ftp_des, remote_dir):
    directories = remote_dir.split('/')
    current_dir = ''
    for directory in directories:
        if directory:
            current_dir = f"{current_dir}/{directory}"
            try:
                ftp_des.mkd(current_dir)
                print(f"Directory created: {current_dir}")
            except error_perm:
                pass
                print(f"Directory already exists: {current_dir}")


def copy_file(ftp_src, ftp_dest, file_path, remote_dir, message):
    remote_file_path = f"{remote_dir}/{os.path.basename(file_path)}"
    create_remote_dir(ftp_dest, remote_dir)

    with open('temp_file', 'wb') as f:
        ftp_src.retrbinary(f'RETR {file_path}', f.write)
    with open('temp_file', 'rb') as f:
        ftp_dest.storbinary(f'STOR {remote_file_path}', f)
    os.remove('temp_file')
    print(f"Successfully {message} {remote_file_path}")


def check_delete(ftp, base_dir, processed_files, processed_dirs):
    REPLICATE_PREFIX = '/home/data_replicate'
    ftp.cwd(base_dir)
    items = ftp.nlst()

    for item in items:
        item_path = os.path.join(base_dir, item)
        is_directory = False
        try:
            ftp.cwd(item_path)  # Try to change to the item directory to check if it's a directory
            is_directory = True
            ftp.cwd('..')  # Move back to the parent directory after checking
        except error_perm:
            pass

        if is_directory:
            if os.path.relpath(item_path, REPLICATE_PREFIX) not in processed_dirs:
                print('rename dirs')
                rename_deleted(ftp, item_path)
            else:
                check_delete(ftp, item_path, processed_files, processed_dirs)  # Recursively check subdirectories
        else:
            if os.path.relpath(item_path, REPLICATE_PREFIX) not in processed_files:
                print('rename files')
                rename_deleted(ftp, item_path)
        ftp.cwd(base_dir)  # Ensure we are back to the base directory


def is_file_modified(ftp, file_path, last_run_time, current_time):
    modified_time = ftp.voidcmd(f"MDTM {file_path}")[4:].strip()
    modified_time = datetime.strptime(modified_time, "%Y%m%d%H%M%S")
    print(
        f"File: {file_path}, Modified Time: {modified_time}, Last Run Time: {last_run_time}, Current Time: {current_time}")
    return last_run_time < modified_time < current_time


def main_process(ftp_source, ftp_replicate, source_base_dir, replicate_base_dir, processed_dirs, processed_files,
                 current_time, last_run_time):
    SOURCE_PREFIX = '/home/data_source'
    ftp_source.cwd(source_base_dir)
    items = ftp_source.nlst()

    for item in items:
        item_path = f"{source_base_dir}/{item}"
        try:
            ftp_source.cwd(item_path)
            processed_dirs.add(item_path[len(SOURCE_PREFIX) + 1:])
            main_process(ftp_source, ftp_replicate, item_path, f"{replicate_base_dir}/{item}", processed_dirs,
                         processed_files, current_time, last_run_time)
            ftp_source.cwd('..')
        except error_perm:
            processed_files.add(item_path[len(SOURCE_PREFIX) + 1:])
            relative_path = os.path.relpath(item_path, source_base_dir)
            dest_path = f"{replicate_base_dir}/{relative_path}"
            dest_dir = os.path.dirname(dest_path)

            # Check if file exist
            # if not any(file == item for file in ftp_replicate.nlst(dest_dir)):
            if not any(os.path.basename(file) == os.path.basename(dest_path) for file in ftp_replicate.nlst(dest_dir)):
                copy_file(ftp_source, ftp_replicate, item_path, dest_dir, 'added')

            # Check if file is modified
            elif is_file_modified(ftp_source, item_path, last_run_time, current_time):
                copy_file(ftp_source, ftp_replicate, item_path, dest_dir, 'updated')


def run_pipeline():
    FTP_SOURCE_DEFAULT_DIR = '/home/data_source'
    FTP_REPLICATE_DEFAULT_DIR = '/home/data_replicate'
    FTP_SOURCE_INFO = FTPManager('localhost', 2121, 'source', 'source', FTP_SOURCE_DEFAULT_DIR)
    FTP_REPLICATE_INFO = FTPManager('localhost', 2122, 'replicate', 'replicate', FTP_REPLICATE_DEFAULT_DIR)

    source_ftp = FTP_SOURCE_INFO.get_connection()
    replicate_ftp = FTP_REPLICATE_INFO.get_connection()

    processed_dirs = set()
    processed_files = set()

    current_time = datetime.now()
    last_run_time = current_time - timedelta(days=1)

    if source_ftp and replicate_ftp:
        main_process(source_ftp, replicate_ftp, FTP_SOURCE_DEFAULT_DIR, FTP_REPLICATE_DEFAULT_DIR, processed_dirs,
                     processed_files, current_time, last_run_time)

        # Handling files/dirs delete
        check_delete(replicate_ftp, FTP_REPLICATE_DEFAULT_DIR, processed_files, processed_dirs)

        # End of pipeline, abort connection
        source_ftp.quit()
        replicate_ftp.quit()


if __name__ == "__main__":
    run_pipeline()
