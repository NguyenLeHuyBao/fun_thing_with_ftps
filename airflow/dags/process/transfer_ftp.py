from ftplib import error_perm
from datetime import datetime
import os
import logging
from libs.connection.ftp_libs import FTPManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def rename_deleted(ftp, path):
    prefix = 'deleted_'
    parent_dir, name = os.path.split(path)
    if not name.startswith(prefix):
        new_name = os.path.join(parent_dir, f"{prefix}{name}")
        try:
            ftp.rename(path, new_name)
            logging.info(f"Renamed {path} to {new_name}")
        except error_perm as e:
            logging.error(f"Failed to rename {path}: {e}")


def create_remote_dir(ftp_des, remote_dir):
    directories = remote_dir.split('/')
    current_dir = ''
    for directory in directories:
        if directory:
            current_dir = f"{current_dir}/{directory}"
            try:
                ftp_des.mkd(current_dir)
                logging.info(f"Directory created: {current_dir}")
            except error_perm:
                pass
                # print(f"Directory already exists: {current_dir}")


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
                logging.info('Renaming file: ' + item_path)
                rename_deleted(ftp, item_path)
        ftp.cwd(base_dir)  # Ensure we are back to the base directory


def is_file_modified(ftp, file_path, last_run_time, current_time):
    modified_time = ftp.voidcmd(f"MDTM {file_path}")[4:].strip()
    modified_time = datetime.strptime(modified_time, "%Y%m%d%H%M%S")
    formatted_modified_time = datetime.strftime(modified_time, "%Y-%m-%d %H:%M:%S")
    logging.info(
        f"File: {file_path}, Modified Time: {modified_time}, Last Run Time: {last_run_time}, Current Time: {current_time}")
    return last_run_time < formatted_modified_time < current_time


def copy_file(ftp_src, ftp_dest, file, source_file_path, remote_dir, message):
    remote_file_path = f"{remote_dir}/{file}"
    create_remote_dir(ftp_dest, remote_dir)

    local_path = os.path.join('/tmp', file)

    try:
        with open(local_path, 'wb') as f:
            ftp_src.retrbinary(f'RETR {source_file_path}', f.write)
        with open(local_path, 'rb') as f:
            ftp_dest.storbinary(f'STOR {remote_file_path}', f)
        os.remove(local_path)
        logging.info(f"Successfully {message} {remote_file_path}")
    except Exception as e:
        logging.error(f"Error {message} {file}: {e}")


def main_process(ftp_source, ftp_replicate, source_base_dir, replicate_base_dir, processed_dirs, processed_files,
                 current_time, last_run_time):
    SOURCE_PREFIX = '/home/data_source'
    file_existed_flag = False

    ftp_source.cwd(source_base_dir)
    items = ftp_source.nlst()

    for item in items:
        item_path = f"{source_base_dir}/{item}"
        try:
            ftp_source.cwd(item_path)
            processed_dirs.add(item_path[len(SOURCE_PREFIX) + 1:])
            main_process(ftp_source, ftp_replicate, f"{source_base_dir}/{item}", f"{replicate_base_dir}/{item}",
                         processed_dirs,
                         processed_files, current_time, last_run_time)
            ftp_source.cwd('..')
        except error_perm:
            processed_files.add(item_path[len(SOURCE_PREFIX) + 1:])
            dest_dir = replicate_base_dir

            # Check if file exist
            for file in ftp_replicate.nlst(dest_dir):
                if item == os.path.basename(file):
                    file_existed_flag = True
                else:
                    continue

            if file_existed_flag:
                logging.info(f"File {item} existed at {dest_dir} --> Check if file has been modified")
                if is_file_modified(ftp_source, item_path, last_run_time, current_time):
                    copy_file(ftp_source, ftp_replicate, item, item_path, dest_dir, 'updated')
            else:
                logging.info(f"File {item} not existed at {dest_dir} --> Create file")
                copy_file(ftp_source, ftp_replicate, item, item_path, dest_dir, 'added')


def transfer_files(**kwargs):
    FTPSourceInfo = kwargs.get('ftp_source')
    FTPReplicateInfo = kwargs.get('ftp_replicate')

    FTP_SOURCE = FTPManager(FTPSourceInfo.host, FTPSourceInfo.port, FTPSourceInfo.usr, FTPSourceInfo.pasw,
                            FTPSourceInfo.default_dir)
    FTP_REPLICATE = FTPManager(FTPReplicateInfo.host, FTPReplicateInfo.port, FTPReplicateInfo.usr,
                               FTPReplicateInfo.pasw,
                               FTPReplicateInfo.default_dir)

    source_ftp = FTP_SOURCE.get_connection()
    replicate_ftp = FTP_REPLICATE.get_connection()

    processed_dirs = set()
    processed_files = set()

    execution_date = kwargs['logical_date']
    next_execution_date = kwargs['next_execution_date']

    current_time = next_execution_date
    last_run_time = execution_date

    current_date = current_time.strftime("%Y-%m-%d %H:%M:%S")
    last_run_date = last_run_time.strftime("%Y-%m-%d %H:%M:%S")

    logging.info(f'Starting running replicate on {current_date}')
    logging.info(f'Last running replicate on {last_run_date}')

    if source_ftp and replicate_ftp:
        main_process(source_ftp, replicate_ftp, FTPSourceInfo.default_dir, FTPReplicateInfo.default_dir, processed_dirs,
                     processed_files, current_date, last_run_date)

        # Handling files/dirs delete
        check_delete(replicate_ftp, FTPReplicateInfo.default_dir, processed_files, processed_dirs)

        # End of pipeline, abort connection
        source_ftp.quit()
        replicate_ftp.quit()
