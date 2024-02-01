import os
import json
import base64
from dotenv import load_dotenv
load_dotenv(".env", verbose=True)
DB_DIRECTORY = os.environ.get('DB_DIRECTORY')


def get_file_path(base_file_name):
    return os.path.join(DB_DIRECTORY, base_file_name)


def encode_username(username):
    return base64.b64encode(username.encode("utf-8")).decode('utf-8')


def save_data_in_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def retrieve_data_from_json(filename):
    with open(filename, "r") as json_file:
        user_data = json.load(json_file)
    return user_data


def save_password_hash(username, hashPassword):
    encoded_username = encode_username(username)
    file_path = get_file_path(f'{encoded_username}.bin')
    with open(file_path, "wb") as file:
        file.write(hashPassword)


def retrieve_password_hash(username):
    encoded_username = encode_username(username)
    file_path = get_file_path(f'{encoded_username}.bin')
    with open(file_path, "rb") as file:
        binary_data = file.read()
    return binary_data


def add_user_data(username, name, surname, hashPassword):
    encoded_username = encode_username(username)
    user_data = {
        "username": username, 
        "name": name,
        "surname": surname
    }
    save_password_hash(username, hashPassword)
    file_path = get_file_path(f'{encoded_username}.json')
    save_data_in_json(file_path, user_data)


def get_user_data(username):
    encoded_username = encode_username(username)
    file_path = get_file_path(f'{encoded_username}.json')
    user_data = retrieve_data_from_json(file_path)
    return user_data


def is_user_exist(username):
    encoded_username = encode_username(username)
    file_path = get_file_path(f'{encoded_username}.json')
    if os.path.exists(file_path):
        return True
    else:
        return False
