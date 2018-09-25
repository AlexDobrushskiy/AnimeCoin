from core_modules.blackbox_modules.keys import id_keypair_generation_func, write_public_and_private_key_to_file_func

from core_modules.rpc_serialization import pack_and_sign, verify_and_unpack


if __name__ == "__main__":
    message_body = ["RPCNAME", "This is some test string"]

    receiver_privkey, receiver_pubkey = id_keypair_generation_func()

    use_require_otp = 0
    # pubkey, privkey = import_public_and_private_keys_from_pem_files_func(use_require_otp)
    privkey, pubkey = id_keypair_generation_func()

    if pubkey == '':
        privkey, pubkey = id_keypair_generation_func()
        write_public_and_private_key_to_file_func(pubkey, privkey)

    raw_msg = pack_and_sign(privkey, pubkey, receiver_pubkey, message_body)

    try:
        sender_id, data = verify_and_unpack(raw_msg, receiver_pubkey)
    except Exception as exc:
        print('Error! Message is NOT valid! Exception: %s' % exc)
    else:
        print('Done! Message has been validated by confirming the digital signature matches the combined message hash.')
        print("sender_id:", sender_id)
        print("data:", data)
