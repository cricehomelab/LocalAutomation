"""
1. Get data from fileinfo.json
2. Get list of movies to upload
3. Connect to jellyfin server with correct access.
4. Path to correct directory
5. Upload file
"""

import json
import os
import logging
import pysftp

#Set logging config
logging.basicConfig(
    filename="upload.log",
    level=logging.DEBUG,
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
            file = f'{directory}\\{file}'
            logging.info(f'Adding {file} to list of files to transfer.')
            files_to_transfer.append(file)
    logging.info("Completed aggregating list of files to transfer returning list.")
    return files_to_transfer

def upload_files(files_to_upload, remote_dir, remote_server, username, private_key):
    '''
    uploads a list of files to the remote Jellyfin server.

        Parameters:
            files_to_upload (list): Fully qualified filepaths of the files we want to upload.
            remote_dir (str): Directory on the remote Jellyfin server we want to upload to.
            remote_server (str): IP address for the Jellyfin server.
            username (str): username for the sftp conncetion.
            private_key (str): private key for the sftp connection.

        Returns:
            None
    '''

    hostname = remote_server
    username = username
    private_key = private_key

    # TODO: This is currently failing and I'm not sure why. Might be a bug based on somethings i Found from last year.
    # going to see if i can dig further. 
    with pysftp.Connection(host=hostname, username=username, private_key=private_key) as sftp:
        logging.info("Established connection to Jellyfin server.")

        for file in files_to_upload:
            logging.info(f'Uploading {file}...')

            remote_directory = remote_dir
            local_filepath = file

            sftp.put(local_filepath, remote_directory)


    logging.info("Files uploaded.")

def main_script():
    logging.info(f"main_script() has been called")
    # TODO: Look to see if i can make this any less hard coded.
    FILE_LOCATION = f"{os.getcwd()}\\AddToJellyfin\\fileinfo.json"

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

    # Seeing what movies are in the file.
    files_to_transfer = get_list_of_files(local_dir)
    logging.info("The following movies will be uploaded:")
    movies = 0
    for movie in files_to_transfer:
        logging.info(f"         {movie}")
        movies += 1
    logging.info(f"Number of Movies to upload: {movies}")

    # Upload data to remote server.
    upload_files(
        files_to_upload=files_to_transfer,
        remote_dir=remote_dir,
        remote_server=remote_server,
        username=remote_username,
        private_key=private_key
    )


main_script()
