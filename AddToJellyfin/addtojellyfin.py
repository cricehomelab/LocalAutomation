"""
1. Get data from fileinfo.json.
2. Get list of movies to upload.
3. Connect to jellyfin server with correct access.
4. Path to correct directory.
5. Upload file.
6. Move files to backup directory.
"""

import json
import os
import logging
import pysftp
import shutil

#Set logging config
logging.basicConfig(
    filename="upload.log",
    level=logging.INFO,
    datefmt='%d-%b-%y %H:%M:%S',
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

def get_json_data(file):
    '''
    Opens the fileinfo.json file and returns the contents of the file.

        Parameters:
            file (str): File path to the fileinfo.json file.

        Returns:
            data (str): Data contained within the fileinfo.json file.
    '''
    print(file)
    logging.info(f"get_json_data({file}) has been called.")
    f = open(file)
    data = json.load(f)
    return data

def get_list_of_files(directory):
    '''
    looks through the files in the directory specified to see if there are .m4v files. If these exist the file is appended
    to a list and once compiled is returned to the main_script function. 

        Parameters:
            directory (str): This is the location of the directory we are searching for .m4v files.

        Returns:
            files_to_transfer (list): This is a list of files that are going to be transferred.
    '''

    logging.info(f"get_list_of_files({directory}) has been called.")
    files_in_directory = os.listdir(directory)
    files_to_transfer = []
    for file in files_in_directory:
        if file.endswith('.m4v'):
            logging.info(f'Adding {file} to list of files to transfer.')
            files_to_transfer.append(file)
    logging.info("Completed aggregating list of files to transfer returning list.")
    return files_to_transfer

def upload_files(files_to_upload, local_dir, remote_dir, remote_server, username, private_key):
    '''
    uploads a list of files to the remote Jellyfin server.

        Parameters:
            files_to_upload (list): Fully qualified filepaths of the files we want to upload.
            remote_dir (str): Directory on the remote Jellyfin server we want to upload to.
            local_dir (str): Local Directory where movies are located.
            remote_server (str): IP address for the Jellyfin server.
            username (str): username for the sftp conncetion.
            private_key (str): private key for the sftp connection.

        Returns:
            None
    '''

    logging.info(f' upload_files({files_to_upload}, {local_dir}, {remote_dir}, {remote_server}, {username}, {private_key}) has been called.')
    hostname = remote_server
    username = username
    private_key = private_key

    # TODO: This is currently failing and I'm not sure why. Might be a bug based on somethings i Found from last year.
    # going to see if i can dig further. 
    with pysftp.Connection(host=hostname, username=username, private_key=private_key) as sftp:
        logging.info("Established connection to Jellyfin server.")

        for file in files_to_upload:
            logging.info(f'Uploading {file}...')

            remote_directory = f'{remote_dir}/{file}'
            local_filepath = f'{local_dir}\\{file}'

            sftp.put(local_filepath, remote_directory)

    logging.info("Files uploaded.")

def move_local_to_backup(files_to_move, current_folder, backup_location):
    '''
    moves files that have been put on the Jellyfin server to the backup folder.
        Parameters:
            files_to_move (list) : List of files that need moved from the copied folder to the backup folder.
            current_folder (str) : Current folder where the files_to_move list resides.
            backup_location (str) : End location for the files we want to move out of the backup folder. 
    '''

    logging.info(f"move_local_to_backup({files_to_move}, {current_folder}, {backup_location}) has been called.")

    for file in files_to_move:
        logging.info(f'Backing up: {file} to {backup_location}')
        current_location = f'{current_folder}\\{file}'
        end_location = f'{backup_location}\\{file}'
        shutil.move(current_location, end_location)


def main_script():
    '''main controller of the scripts running.'''

    logging.info(f"main_script() has been called")

    # TODO: Look to see if i can make this any less hard coded.
    FILE_LOCATION = f'{os.getcwd()}\\AddToJellyfin\\fileinfo.json'
    print(FILE_LOCATION)

    # Getting data from JSON and putting into variables. 
    json_data = get_json_data(FILE_LOCATION)
    remote_server = json_data['remote_server']
    logging.debug(f'Remote server address: {remote_server}')
    private_key = json_data['remote_server_private_key']
    logging.debug(f'Remote server private key location: {private_key}')
    local_dir = json_data['movie_local_dir']
    logging.debug(f'Local directory we are checkng for movies: {local_dir}')
    remote_dir = json_data['remote_server_movie_dir']
    logging.debug(f'Remote directory we are uploading movies to: {remote_dir}')
    remote_username = json_data['remote_server_username']
    logging.debug(f"Remote server username is: {remote_username}")
    backup_location = json_data['backup_folder_location']
    logging.debug(f'Backup folder location: {backup_location}')

    # Seeing what movies are in the file.
    files_to_transfer = get_list_of_files(local_dir)
    logging.info("The following movies will be uploaded:")
    movies = 0
    for movie in files_to_transfer:
        logging.info(f"         {movie}")
        movies += 1
    logging.info(f"Number of Movies to upload: {movies}")

    if movies == 0:
        logging.info(f'There are no movies to upload. Ending')
        return None

    # Upload data to remote server.
    upload_files(
        files_to_upload=files_to_transfer,
        local_dir=local_dir,
        remote_dir=remote_dir,
        remote_server=remote_server,
        username=remote_username,
        private_key=private_key
    )

    # Move the remaining copy to the backup folder.
    move_local_to_backup(
        files_to_move=files_to_transfer,
        current_folder=local_dir,
        backup_location=backup_location
    )

main_script()
