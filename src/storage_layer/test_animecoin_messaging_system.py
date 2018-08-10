import glob
import os


from animecoin_modules.animecoin_keys import import_animecoin_public_and_private_keys_from_pem_files_func, \
    animecoin_id_keypair_generation_func, write_animecoin_public_and_private_key_to_file_func
from animecoin_modules.animecoin_messenger_object import generate_message_func, verify_compressed_message_file,\
    read_unverified_compressed_message_file, verify_raw_message_file


if __name__ == "__main__":
    message_body = ""
    message_body = "1234"
    message_body = "Crud far in far oh immoral and more caribou hiccupped tyrannically tortoise rode sheepishly where gorilla metric radical the badger a and gosh smugly manatee devilishly that."
    message_body = "Above occasional as sang however jeepers vengeful pounded dashingly smugly far studied anteater darn yet unbound more reprehensively and watchful hello ingenuously nightingale between less the much gloated then and less."
    message_body = "Coasted more dipped ouch in hey stupid one monumental more so suddenly precisely and a far audible leniently ocelot thanks changed goodness toward well next jeez."
    message_body = "Since grimaced modest rode unwound notwithstanding expressly one devilish that decided off alas as goodness wow wayward robin that a one customarily cassowary within spoiled."
    message_body = "Beseechingly from much well reindeer glib erect nobly opossum and abject darn lemur so a in neutrally more indescribably meticulous that more after wow while jeez this roadrunner ouch for reasonable less unwittingly."
    message_body = "This is a test of our new messaging system. We hope that it's secure from attacks. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

    test_receiver__animecoin_id_private_key_b16_encoded, test_receiver__animecoin_id_public_key_b16_encoded = animecoin_id_keypair_generation_func()
    target_pubkey = test_receiver__animecoin_id_public_key_b16_encoded

    use_require_otp = 0
    pubkey, privkey = import_animecoin_public_and_private_keys_from_pem_files_func(use_require_otp)

    if pubkey == '':
        privkey, pubkey = animecoin_id_keypair_generation_func()
        write_animecoin_public_and_private_key_to_file_func(pubkey, privkey)

    raw_msg, signed_msg, signature = generate_message_func(privkey, pubkey, target_pubkey, message_body)

    verified, senders_animecoin_id, receivers_animecoin_id, timestamp_of_message, message_size, message_body, random_nonce, signature_line = verify_raw_message_file(
        raw_msg)

    if verified:
        print('Done! Message has been validated by confirming the digital signature matches the combined message hash.')
    else:
        print('Error! Message is NOT valid!')

    use_require_otp = 0
    senders_animecoin_id, _ = import_animecoin_public_and_private_keys_from_pem_files_func(use_require_otp)
    decompressed_message_data = verify_compressed_message_file(senders_animecoin_id,
                                                                                signed_msg,
                                                                                signature)
    verified, senders_animecoin_id, receivers_animecoin_id, timestamp_of_message, message_size, message_body, random_nonce, signature_line = verify_raw_message_file(
        decompressed_message_data)
    if verified:
        print(
            'Done! Compressed message has been validated by confirming the digital signature matches the combined message hash.')
    else:
        print('Error! Message is NOT valid!')

    print('Now testing unverified compressed file read functionality...')
    decompressed_message_data = read_unverified_compressed_message_file(signed_msg)
    if isinstance(decompressed_message_data, str):
        print('Successfully read unverified compressed file!')
    else:
        print('Error!')
