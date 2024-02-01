import os
import json
import base64


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
    print("---------------*******", hashPassword)
    encoded_username = encode_username(username)
    with open(f'db/{encoded_username}.bin', "wb") as file:
        file.write(hashPassword)


def retrieve_password_hash(username):
    encoded_username = encode_username(username)
    with open(f'db/{encoded_username}.bin', "rb") as file:
        binary_data = file.read()
    return binary_data


# def check_password_hash(username, hashPassword):
#     encoded_username = encode_username(username)
#     retrieve_password_hash = retrieve_binary_data(f'db/{encoded_username}.bin')
#     if hashPassword == retrieve_password_hash:
#         return True
#     else:
#         return False


def add_user_data(username, name, surname, hashPassword):
    encoded_username = encode_username(username)
    user_data = {
        "username": username, 
        "name": name,
        "surname": surname
    }
    save_password_hash(username, hashPassword)
    save_data_in_json(f'db/{encoded_username}.json', user_data)


def get_user_data(username):
    encoded_username = encode_username(username)
    filename = f'db/{encoded_username}.json'
    user_data = retrieve_data_from_json(filename)
    return user_data


def is_user_exist(username):
    encoded_username = encode_username(username)
    if os.path.exists(f'db/{encoded_username}.json'):
        return True
    else:
        return False
