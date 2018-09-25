import os
import nacl
import base64

from nacl import utils, secret

from .helpers import Timer
from .otp import generate_current_otp_string_func, generate_current_otp_string_from_user_input_func
from .secure_storage import get_nacl_box_key_from_environment_or_file_func, get_nacl_box_key_from_user_input_func
from .crypto import get_Ed521

Ed521 = get_Ed521()


def import_public_and_private_keys_from_pem_files_func(use_require_otp):
    # use_require_otp = 1
    keys_storage_folder_path = os.getcwd() + os.sep + 'key_files' + os.sep
    if not os.path.isdir(keys_storage_folder_path):
        print("Can't find key storage directory, trying to use current working directory instead!")
        keys_storage_folder_path = os.getcwd() + os.sep
    public_key_pem_filepath = keys_storage_folder_path + 'ed521_public_key.pem'
    private_key_pem_filepath = keys_storage_folder_path + 'ed521_private_key.pem'
    if (os.path.isfile(public_key_pem_filepath) and os.path.isfile(private_key_pem_filepath)):
        with open(public_key_pem_filepath, 'r') as f:
            public_key_export_format = f.read()
        with open(private_key_pem_filepath, 'rb') as f:
            private_key_export_format__encrypted = f.read()
        if use_require_otp:
            try:
                otp_string = generate_current_otp_string_func()
            except:
                otp_string = generate_current_otp_string_from_user_input_func()
            otp_from_user_input = input('\nPlease Enter your Google Authenticator Code:\n\n')
            assert (len(otp_from_user_input) == 6)
            otp_correct = (otp_from_user_input == otp_string)
        else:
            otp_correct = True

        if otp_correct:
            try:
                box_key = get_nacl_box_key_from_environment_or_file_func()
            except:
                print("\n\nCan't find OTP secret in environment variables! Enter Secret below:\n\n")
                box_key = get_nacl_box_key_from_user_input_func()
            box = nacl.secret.SecretBox(box_key)
            public_key_b16_encoded = public_key_export_format.replace(
                "-----BEGIN ED521 PUBLIC KEY-----\n", "").replace("\n-----END ED521 PUBLIC KEY-----", "")
            private_key_export_format = box.decrypt(private_key_export_format__encrypted)
            private_key_export_format = private_key_export_format.decode('utf-8')
            private_key_b16_encoded = private_key_export_format.replace(
                "-----BEGIN ED521 PRIVATE KEY-----\n", "").replace("\n-----END ED521 PRIVATE KEY-----", "")
    else:
        public_key_b16_encoded = ''
        private_key_b16_encoded = ''
    return public_key_b16_encoded, private_key_b16_encoded


def write_public_and_private_key_to_file_func(public_key_b16_encoded, private_key_b16_encoded):
    public_key_export_format = "-----BEGIN ED521 PUBLIC KEY-----\n" + public_key_b16_encoded + "\n-----END ED521 PUBLIC KEY-----"
    private_key_export_format = "-----BEGIN ED521 PRIVATE KEY-----\n" + private_key_b16_encoded + "\n-----END ED521 PRIVATE KEY-----"
    try:
         box_key = get_nacl_box_key_from_environment_or_file_func()
    except:
        print("\n\nCan't find OTP secret in environment variables! Enter Secret below:\n\n")
        box_key = get_nacl_box_key_from_user_input_func()
    box = nacl.secret.SecretBox(box_key) # This is your safe, you can use it to encrypt or decrypt messages
    private_key_export_format__encrypted = box.encrypt(private_key_export_format.encode('utf-8'))
    keys_storage_folder_path = os.getcwd() + os.sep + 'key_files' + os.sep
    if not os.path.isdir(keys_storage_folder_path):
        try:
            os.makedirs(keys_storage_folder_path)
        except:
            print('Error creating directory-- instead saving to current working directory!')
            keys_storage_folder_path = os.getcwd() + os.sep
    with open(keys_storage_folder_path + 'ed521_public_key.pem','w') as f:
        f.write(public_key_export_format)
    with open(keys_storage_folder_path + 'ed521_private_key.pem','wb') as f:
        f.write(private_key_export_format__encrypted)


def id_keypair_generation_func():
    input_length = 521*2
    private_key, public_key = Ed521.keygen(nacl.utils.random(input_length))
    private_key_b16_encoded = base64.b16encode(private_key).decode('utf-8')
    public_key_b16_encoded = base64.b16encode(public_key).decode('utf-8')
    return private_key_b16_encoded, public_key_b16_encoded


def generate_and_store_key_for_nacl_box_func():
    box_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)  # This must be kept secret, this is the combination to your safe
    box_key_base64 = base64.b64encode(box_key).decode('utf-8')
    with open('box_key.bin','w') as f:
        f.write(box_key_base64)
    print('This is the key for encrypting the Pastel ID private key (using NACL box) in Base64: '+ box_key_base64)
    print('The key has been stored as an environment varibale on the local machine and saved as a file in the working directory. You should also write this key down as a backup.')
    os.environ['NACL_KEY'] = box_key_base64
