import os
import nacl
import base64

from nacl import utils, secret

from .helpers import AnimeTimer
from .animecoin_otp import generate_current_otp_string_func, generate_current_otp_string_from_user_input_func
from .animecoin_secure_storage import get_nacl_box_key_from_environment_or_file_func, get_nacl_box_key_from_user_input_func
from .animecoin_crypto import get_Ed521

Ed521 = get_Ed521()


def import_animecoin_public_and_private_keys_from_pem_files_func(use_require_otp):
    # use_require_otp = 1
    animecoin_id_keys_storage_folder_path = os.getcwd() + os.sep + 'animecoin_id_key_files' + os.sep
    if not os.path.isdir(animecoin_id_keys_storage_folder_path):
        print("Can't find key storage directory, trying to use current working directory instead!")
        animecoin_id_keys_storage_folder_path = os.getcwd() + os.sep
    animecoin_id_public_key_pem_filepath = animecoin_id_keys_storage_folder_path + 'animecoin_id_ed521_public_key.pem'
    animecoin_id_private_key_pem_filepath = animecoin_id_keys_storage_folder_path + 'animecoin_id_ed521_private_key.pem'
    if (os.path.isfile(animecoin_id_public_key_pem_filepath) and os.path.isfile(animecoin_id_private_key_pem_filepath)):
        with open(animecoin_id_public_key_pem_filepath, 'r') as f:
            animecoin_id_public_key_export_format = f.read()
        with open(animecoin_id_private_key_pem_filepath, 'rb') as f:
            animecoin_id_private_key_export_format__encrypted = f.read()
        if use_require_otp:
            try:
                otp_string = generate_current_otp_string_func()
            except:
                otp_string = generate_current_otp_string_from_user_input_func()
            otp_from_user_input = input('\nPlease Enter your Animecoin Google Authenticator Code:\n\n')
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
            animecoin_id_public_key_b16_encoded = animecoin_id_public_key_export_format.replace(
                "-----BEGIN ED521 PUBLIC KEY-----\n", "").replace("\n-----END ED521 PUBLIC KEY-----", "")
            animecoin_id_private_key_export_format = box.decrypt(animecoin_id_private_key_export_format__encrypted)
            animecoin_id_private_key_export_format = animecoin_id_private_key_export_format.decode('utf-8')
            animecoin_id_private_key_b16_encoded = animecoin_id_private_key_export_format.replace(
                "-----BEGIN ED521 PRIVATE KEY-----\n", "").replace("\n-----END ED521 PRIVATE KEY-----", "")
    else:
        animecoin_id_public_key_b16_encoded = ''
        animecoin_id_private_key_b16_encoded = ''
    return animecoin_id_public_key_b16_encoded, animecoin_id_private_key_b16_encoded


def write_animecoin_public_and_private_key_to_file_func(animecoin_id_public_key_b16_encoded, animecoin_id_private_key_b16_encoded):
    animecoin_id_public_key_export_format = "-----BEGIN ED521 PUBLIC KEY-----\n" + animecoin_id_public_key_b16_encoded + "\n-----END ED521 PUBLIC KEY-----"
    animecoin_id_private_key_export_format = "-----BEGIN ED521 PRIVATE KEY-----\n" + animecoin_id_private_key_b16_encoded + "\n-----END ED521 PRIVATE KEY-----"
    try:
         box_key = get_nacl_box_key_from_environment_or_file_func()
    except:
        print("\n\nCan't find OTP secret in environment variables! Enter Secret below:\n\n")
        box_key = get_nacl_box_key_from_user_input_func()
    box = nacl.secret.SecretBox(box_key) # This is your safe, you can use it to encrypt or decrypt messages
    animecoin_id_private_key_export_format__encrypted = box.encrypt(animecoin_id_private_key_export_format.encode('utf-8'))
    animecoin_id_keys_storage_folder_path = os.getcwd() + os.sep + 'animecoin_id_key_files' + os.sep
    if not os.path.isdir(animecoin_id_keys_storage_folder_path):
        try:
            os.makedirs(animecoin_id_keys_storage_folder_path)
        except:
            print('Error creating directory-- instead saving to current working directory!')
            animecoin_id_keys_storage_folder_path = os.getcwd() + os.sep
    with open(animecoin_id_keys_storage_folder_path + 'animecoin_id_ed521_public_key.pem','w') as f:
        f.write(animecoin_id_public_key_export_format)
    with open(animecoin_id_keys_storage_folder_path + 'animecoin_id_ed521_private_key.pem','wb') as f:
        f.write(animecoin_id_private_key_export_format__encrypted)


def animecoin_id_keypair_generation_func():
    print('Generating Eddsa 521 keypair now...')
    with AnimeTimer():
        input_length = 521*2
        animecoin_id_private_key, animecoin_id_public_key = Ed521.keygen(nacl.utils.random(input_length))
        animecoin_id_private_key_b16_encoded = base64.b16encode(animecoin_id_private_key).decode('utf-8')
        animecoin_id_public_key_b16_encoded = base64.b16encode(animecoin_id_public_key).decode('utf-8')
        return animecoin_id_private_key_b16_encoded, animecoin_id_public_key_b16_encoded


def generate_and_store_key_for_nacl_box_func():
    box_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)  # This must be kept secret, this is the combination to your safe
    box_key_base64 = base64.b64encode(box_key).decode('utf-8')
    with open('box_key.bin','w') as f:
        f.write(box_key_base64)
    print('This is the key for encrypting the Animecoin ID private key (using NACL box) in Base64: '+ box_key_base64)
    print('The key has been stored as an environment varibale on the local machine and saved as a file in the working directory. You should also write this key down as a backup.')
    os.environ['NACL_KEY'] = box_key_base64
