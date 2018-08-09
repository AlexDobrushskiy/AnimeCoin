import io
import os
import base64
import pyqrcode
import PIL
import pyotp


def regenerate_google_auth_qr_code_from_secret_func():
    otp_secret = input('Enter your Google Authenticator Secret in all upper case and numbers:\n')
    otp_secret_character_set = 'ABCDEF1234567890'
    assert(len(otp_secret)==16)
    assert([(x in otp_secret_character_set) for x in otp_secret])
    totp = pyotp.totp.TOTP(otp_secret)
    google_auth_uri = totp.provisioning_uri("user@user.com", issuer_name="Animecoin")
    qr_error_correcting_level = 'M' # L, M, Q, H
    qr_encoding_type = 'binary'
    qr_scale_factor = 6
    google_auth_qr_code = pyqrcode.create(google_auth_uri, error=qr_error_correcting_level, version=16, mode=qr_encoding_type)
    google_auth_qr_code_png_string = google_auth_qr_code.png_as_base64_str(scale=qr_scale_factor)
    google_auth_qr_code_png_data = base64.b64decode(google_auth_qr_code_png_string)
    pil_qr_code_image = PIL.Image.open(io.BytesIO(google_auth_qr_code_png_data))
    pil_qr_code_image.show()
    return otp_secret


def set_up_google_authenticator_for_private_key_encryption_func():
    secret = pyotp.random_base32() # returns a 16 character base32 secret. Compatible with Google Authenticator and other OTP apps
    os.environ['ANIME_OTP_SECRET'] = secret
    with open('otp_secret.txt','w') as f:
        f.write(secret)
    totp = pyotp.totp.TOTP(secret)
    #google_auth_uri = urllib.parse.quote_plus(totp.provisioning_uri("user@domain.com", issuer_name="Animecoin"))
    google_auth_uri = totp.provisioning_uri("user@user.com", issuer_name="Animecoin")
    #current_otp = totp.now()
    qr_error_correcting_level = 'M' # L, M, Q, H
    qr_encoding_type = 'binary'
    qr_scale_factor = 6
    google_auth_qr_code = pyqrcode.create(google_auth_uri, error=qr_error_correcting_level, version=16, mode=qr_encoding_type)
    google_auth_qr_code_png_string = google_auth_qr_code.png_as_base64_str(scale=qr_scale_factor)
    google_auth_qr_code_png_data = base64.b64decode(google_auth_qr_code_png_string)
    pil_qr_code_image = PIL.Image.open(io.BytesIO(google_auth_qr_code_png_data))
    img_width, img_height = pil_qr_code_image.size #getting the base image's size
    if pil_qr_code_image.mode != 'RGB':
        pil_qr_code_image = pil_qr_code_image.convert("RGB")
    pil_qr_code_image = PIL.ImageOps.expand(pil_qr_code_image, border=(600,300,600,0))
    drawing_context = PIL.ImageDraw.Draw(pil_qr_code_image)
    font1 = PIL.ImageFont.truetype('FreeSans.ttf', 30)
    font2 = PIL.ImageFont.truetype('FreeSans.ttf', 20)
    warning_message = 'Warning! Once you close this window, this QR code will be lost! You should write down your Google Auth URI string (shown below) as a backup, which will allow you to regenerate the QR code image.'
    drawing_context.text((50,65), google_auth_uri,(255,255,255),font=font1)
    drawing_context.text((50,5), warning_message,(255,255,255),font=font2)
    pil_qr_code_image.show()


def generate_qr_codes_from_animecoin_keypair_func(animecoin_id_public_key_b16_encoded, animecoin_id_private_key_b16_encoded):
    qr_error_correcting_level = 'M' # L, M, Q, H
    qr_encoding_type = 'alphanumeric'
    qr_scale_factor = 6
    animecoin_id_public_key_b16_encoded_qr_code = pyqrcode.create(animecoin_id_public_key_b16_encoded, error=qr_error_correcting_level, version=16, mode=qr_encoding_type)
    animecoin_id_private_key_b16_encoded_qr_code = pyqrcode.create(animecoin_id_private_key_b16_encoded, error=qr_error_correcting_level, version=31, mode=qr_encoding_type)
    animecoin_id_keys_storage_folder_path = os.getcwd() + os.sep + 'animecoin_id_key_files' + os.sep
    if not os.path.isdir(animecoin_id_keys_storage_folder_path):
        try:
            os.makedirs(animecoin_id_keys_storage_folder_path)
        except:
            print('Error creating directory-- instead saving to current working directory!')
            animecoin_id_keys_storage_folder_path = os.getcwd() + os.sep
    animecoin_id_public_key_b16_encoded_qr_code.png(file=animecoin_id_keys_storage_folder_path + 'animecoin_id_ed521_public_key_qr_code.png', scale=qr_scale_factor)
    animecoin_id_private_key_b16_encoded_qr_code.png(file=animecoin_id_keys_storage_folder_path + 'animecoin_id_ed521_private_key_qr_code.png',scale=qr_scale_factor)
