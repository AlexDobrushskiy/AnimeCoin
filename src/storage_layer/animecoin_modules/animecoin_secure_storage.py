import os
import base64


def get_nacl_box_key_from_user_input_func():
    box_key_base64 = input('\n\nEnter your NACL box key in Base64:\n\n')
    assert(len(box_key_base64) == 44)
    box_key = base64.b64decode(box_key_base64)
    return box_key


def get_nacl_box_key_from_environment_or_file_func():
    try:
        box_key_base64 = os.environ['NACL_KEY']
    except KeyError:
        with open('box_key.bin', 'r') as f:
            box_key_base64 = f.read()
    assert(len(box_key_base64) == 44)
    box_key = base64.b64decode(box_key_base64)
    return box_key
