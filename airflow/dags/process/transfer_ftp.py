from ftplib import FTP, error_perm
import socket
import os
from libs.connection.ftp_libs import FTPManager


# def connect_ftp(ftp_info):
#     try:
#         ftp = FTP()
#         ftp.connect(ftp_info.host, ftp_info.port, timeout=30)
#         ftp.login(ftp_info.usr, ftp_info.passwd)
#         ftp.set_pasv(True)
#         ftp.cwd(ftp_info.base_dir)
#         print(f"Connected to {ftp_info.host}:{ftp_info.port}")
#         print("Directory contents:", ftp.nlst())
#         return ftp
#     except (socket.timeout, ConnectionRefusedError) as e:
#         print(f"Failed to connect to {ftp_info.host}:{ftp_info.port} - {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     return None


def download_file(ftp, filename, local_path):
    with open(local_path, 'wb') as f:
        ftp.retrbinary(f"RETR {filename}", f.write)


def upload_file(ftp, local_path, filename):
    with open(local_path, 'rb') as f:
        ftp.storbinary(f"STOR {filename}", f)


def file_exists(ftp, filename):
    try:
        ftp.size(filename)
        return True
    except error_perm as e:
        if '550' in str(e):
            return False
        raise


def dir_exists(ftp, dir_name):
    current = ftp.pwd()
    try:
        ftp.cwd(dir_name)
        ftp.cwd(current)
        return True
    except error_perm as e:
        if '550' in str(e):
            return False
        raise


def create_directory(ftp, dirname):
    try:
        ftp.mkd(dirname)
    except error_perm as e:
        if '550' in str(e):
            print(f"Directory {dirname} already exists on the destination FTP server")
        else:
            raise


def delete_file(ftp, filename):
    try:
        ftp.delete(filename)
    except error_perm as e:
        if '550' in str(e):
            print(f"File {filename} does not exist on the destination FTP server")
        else:
            raise


def delete_directory(ftp, dirname):
    ftp.cwd(dirname)
    files, dirs = list_files_dirs(ftp)

    for file in files:
        delete_file(ftp, file)

    for dir in dirs:
        delete_directory(ftp, dir)

    ftp.cwd('..')
    ftp.rmd(dirname)


def list_files_dirs(ftp):
    file_list = []
    dir_list = []
    ftp.retrlines('LIST',
                  lambda x: file_list.append(x.split()[-1]) if x.startswith('-') else dir_list.append(x.split()[-1]))
    return file_list, dir_list


def transfer_items(source_ftp, destination_ftp, source_base_dir, dest_base_dir):
    source_ftp.cwd(source_base_dir)
    destination_ftp.cwd(dest_base_dir)

    source_files, source_dirs = list_files_dirs(source_ftp)
    dest_files, dest_dirs = list_files_dirs(destination_ftp)

    for file in source_files:
        local_path = os.path.join('/tmp', file)
        if not file_exists(destination_ftp, file):
            print(f"Transferring file: {file} from {source_base_dir}")
            download_file(source_ftp, file, local_path)
            upload_file(destination_ftp, local_path, file)
            os.remove(local_path)
        else:
            print(f"File {file} already exists on the destination FTP server")

    for dir in source_dirs:
        if not dir_exists(destination_ftp, dir):
            print(f"Creating directory: {dir} in {source_base_dir}")
            create_directory(destination_ftp, dir)
        transfer_items(source_ftp, destination_ftp, os.path.join(source_base_dir, dir),
                       os.path.join(dest_base_dir, dir))
        destination_ftp.cwd('..')

    for file in dest_files:
        if file not in source_files:
            print(f"Deleting file: {file} from {dest_base_dir}")
            delete_file(destination_ftp, file)

    for dir in dest_dirs:
        if dir not in source_dirs:
            print(f"Deleting directory: {dir} from {dest_base_dir}")
            delete_directory(destination_ftp, dir)


def transfer_files():
    FTP_SOURCE_INFO = FTPManager('ftp-server', 21, 'source', 'source', '/home/data_source')
    FTP_REPLICATE_INFO = FTPManager('ftp-replicate', 21, 'replicate', 'replicate', '/home/data_replicate')

    source_ftp = FTP_SOURCE_INFO.get_connection()
    destination_ftp = FTP_REPLICATE_INFO.get_connection()
    if source_ftp and destination_ftp:
        transfer_items(source_ftp, destination_ftp, FTP_SOURCE_INFO.base_dir, FTP_REPLICATE_INFO.base_dir)
        source_ftp.quit()
        destination_ftp.quit()
