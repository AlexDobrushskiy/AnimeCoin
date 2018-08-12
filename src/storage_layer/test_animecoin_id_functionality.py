from dht_prototype.animecoin_modules.animecoin_crypto import get_Ed521
from dht_prototype.animecoin_modules.animecoin_keys import import_animecoin_public_and_private_keys_from_pem_files_func, \
    animecoin_id_keypair_generation_func, write_animecoin_public_and_private_key_to_file_func
from dht_prototype.animecoin_modules.animecoin_qrcode import generate_qr_codes_from_animecoin_keypair_func
from dht_prototype.animecoin_modules.animecoin_signatures import animecoin_id_write_signature_on_data_func, \
    animecoin_id_verify_signature_with_public_key_func

# Dependencies: pip install nacl pyqrcode
# Eddsa code is from the RFC documentation: https://datatracker.ietf.org/doc/html/rfc8032


Ed521 = get_Ed521()

use_demonstrate_eddsa_crypto = 0

if use_demonstrate_eddsa_crypto:
    # Example using a fake artwork combined metadata string:
    input_data_text = "1.00 || 2018-05-20 17:01:17:110168 || 523606 || 0000000000000000002c65b5e9be26fba6e0fb2ed9e665f567260ee14bb0d390 || 2512 || 00000000000000000020cf882b78a089514eb19583b36171e62b16994f94e6b7 || -----BEGIN ED521 PRIVATE KEY-----3677B6B51908E462367834786C9E9D4D277BBD96988AD228C30787E183DCC698E59DEBC0E1DB5F636893DE484281F9B96651B3D431DF5C60050C9F799E6251092C7A72282EAD69DF7191F4C24C853CC4C8AD2A24B6ED833AD98C55BC27D4C654B6FD0010A8D832C057731C7D3A6567BB09C0FE83420D7949493FAB2129B0935BAD47BCB6C1159B66F23953DE280AD2D2BD954FB7A589C3FEF4E6056317BA9AE9BA82AB7D4C0C501893BCA3329642DBBF8C9BFE555B2AAB9500B1DAD3BC5D973234C9C734A6F9D2FDA6024F5354ED373B5981910D6DA69BECCCF6C641C00E47AD019793F33A2404D87D8E794D885C4A168B1017ECA715A42F4CD9D6BAAB5F252ECB5B1BC8402A2F6937F72CED3E4658C5AA4CF0DDA29F28A3731D2C006F836DFD05603F121E7C93625496BB942564C33A23CF8FD30BF9939D83E45C7CCF955440AF7E888024E4EBF91D12160001DDBC9CA31D045DF997F73D4A74AF3464C46BBEAE88A1F4F9290823B6994824C181E72C7FD7D084BC2E5675257BC1888E3C8A67EA1DA28DBE2D5F796B019700D4D0838CCA376426120B93733A8F6C3D5AFEEA2D869366C4CBA51A10B6838A171BCC8F2C8D079A75DC783AAB1A0E0DF66CD371316DBF9F8E4A8D3B5B9FDE1DC1C0E70259BEED1936D0B9196C9766C6A02F0EDA929166550E3E7FBD27E366FAC350D2F6D09010BA8ECD6F2139B9B45BF1FE0AFE69E49D44C3F5D76E8AA531EBBA50B55A44C41AD5B7A216595AC1A8A805236E8EDFB5D84B0B56AC7F1B376470E8B891A38A85FA3F6BBE252C8E2AA447B56C40235DA6EE7D5C7812410A301737BFCB0E461F8B0B1587DE3A6C99AFD4108D51778C4D5C42568010806E873E49565DEAA8204A17C71688148CD346BE9AD17B1A26920172A079C5322EBC931BB35EC5387223B6FEA7BE46B6D13CDE62D42E2EB64643047E7829205E36762FE061DE43D5A78270A16B46A87DAC58FC77749615033529435220A1D9BF651187DB8E1A2C2D568FA4001F6F9E8A2A242037118B0A8D89F6133A186C7ADAF6D06A5CE698D3F8466C9FF041BE42C576BD9EA1F514272D6D33E73A1D8373E88F178A18420B39C59818E1BD7B5E56CEC50AC6C668643BA80096F2D9B1D864833FD875DE6CD1E943C024CE0B729A150A59FA5D498D62A47B8E54C210BCC275EAB7541AED477C86BAE4BB8FF487D05298607E04281154E713ED86D17CB03ADCEFB923DCF6BEAF8E79A47306C1F52B770F6D4F0FF8E9FB63F8048B64FF308C0324FB47E9771C3C5E9CD2E72763C0A8E6F5B358D8BE20CE248C1258CD1B0291D3F039E1761CC86483DB417ED680C1A7494219431E76D75866E5FC2D55E4C9493D836E78FF336569CC3482264D11B14A4EDD49919E25ADF7135FF70C9BE5900E1A0D0C8F732E5E6E463EFBD325A7F3A893BD7D7A33B38AF0B8A3CBCFE2E0D45C2372B7B32D21DAB319CDB196C3EC83-----END ED521 PRIVATE KEY-----|| 500 || Magnificent Vampire: Evil 2 || Mark Kong || || https://foxykuro.deviantart.com/ || I have been drawing since I was young! I hope everyone likes my newest works, I have been learning how to use a tablet! Hit me up on discord, username is AnimeFreak15! Thx!!! || 12.415804 || 514a10f0eec73108685ff60c8481bf8343b934fb1e5ab0f6020812ec683739f2 || 350 || 100 || 3.5 || 149 || 43 || 4 ||"
    input_data = input_data_text.encode('utf-8')
    use_require_otp = 0
    animecoin_id_public_key_b16_encoded, animecoin_id_private_key_b16_encoded = import_animecoin_public_and_private_keys_from_pem_files_func(
        use_require_otp)
    if animecoin_id_public_key_b16_encoded == '':
        animecoin_id_private_key_b16_encoded, animecoin_id_public_key_b16_encoded = animecoin_id_keypair_generation_func()
        write_animecoin_public_and_private_key_to_file_func(animecoin_id_public_key_b16_encoded,
                                                            animecoin_id_private_key_b16_encoded)
        generate_qr_codes_from_animecoin_keypair_func(animecoin_id_public_key_b16_encoded,
                                                      animecoin_id_private_key_b16_encoded)
    animecoin_id_signature_b16_encoded = animecoin_id_write_signature_on_data_func(input_data,
                                                                                   animecoin_id_private_key_b16_encoded,
                                                                                   animecoin_id_public_key_b16_encoded)
    verified = animecoin_id_verify_signature_with_public_key_func(input_data, animecoin_id_signature_b16_encoded,
                                                                  animecoin_id_public_key_b16_encoded)
