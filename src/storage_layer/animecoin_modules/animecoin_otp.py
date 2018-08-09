import os
import pyotp


def generate_current_otp_string_func():
    try:
        otp_secret = os.environ['ANIME_OTP_SECRET']
    except KeyError:
        with open('otp_secret.txt', 'r') as f:
            otp_secret = f.read()
    otp_secret_character_set = 'ABCDEF1234567890'
    assert(len(otp_secret) == 16)
    assert([(x in otp_secret_character_set) for x in otp_secret])
    totp = pyotp.totp.TOTP(otp_secret)
    current_otp = totp.now()
    return current_otp


def generate_current_otp_string_from_user_input_func():
    otp_secret = input('\n\nEnter your Google Authenticator Secret in all upper case and numbers:\n\n')
    otp_secret_character_set = 'ABCDEF1234567890'
    assert(len(otp_secret) == 16)
    assert([(x in otp_secret_character_set) for x in otp_secret])
    totp = pyotp.totp.TOTP(otp_secret)
    current_otp = totp.now()
    return current_otp
