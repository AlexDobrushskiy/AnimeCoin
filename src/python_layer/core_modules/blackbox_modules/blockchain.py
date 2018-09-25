import binascii
import io
import sys
import struct
import random
from binascii import unhexlify, hexlify
from decimal import Decimal

from core_modules.helpers import get_hexdigest, get_digest
from core_modules.settings import NetWorkSettings

base_transaction_amount = 0.000001
FEEPERKB = Decimal(0.0001)
COIN = NetWorkSettings.COIN


OP_CHECKSIG = b'\xac'
OP_CHECKMULTISIG = b'\xae'
OP_PUSHDATA1 = b'\x4c'
OP_DUP = b'\x76'
OP_HASH160 = b'\xa9'
OP_EQUALVERIFY = b'\x88'


def unhexstr(str):
    return unhexlify(str.encode('utf8'))


def select_txins(value, unspent):
    # TODO: make sure this is always one input!
    random.shuffle(unspent)
    r = []
    total = 0
    for tx in unspent:
        total += tx['amount']
        r.append(tx)
        if total >= value:
            break
    if total < value:
        return None
    else:
        return (r, total)


def varint(n):
    if n < 0xfd:
        return bytes([n])
    elif n < 0xffff:
        return b'\xfd' + struct.pack('<H', n)
    else:
        assert False


def packtxin(prevout, scriptSig, seq=0xffffffff):
    return prevout[0][::-1] + struct.pack('<L', prevout[1]) + varint(len(scriptSig)) + scriptSig + struct.pack('<L',
                                                                                                               seq)


def packtxout(value, scriptPubKey):
    return struct.pack('<Q', int(value * COIN)) + varint(len(scriptPubKey)) + scriptPubKey


def packtx(txins, txouts, locktime=0):
    r = b'\x01\x00\x00\x00'  # version
    r += varint(len(txins))
    for txin in txins:
        r += packtxin((unhexstr(txin['txid']), txin['vout']), b'')
    r += varint(len(txouts))
    for (value, scriptPubKey) in txouts:
        r += packtxout(value, scriptPubKey)
    r += struct.pack('<L', locktime)
    return r


def pushdata(data):
    assert len(data) < OP_PUSHDATA1[0]
    return bytes([len(data)]) + data


def pushint(n):
    assert 0 < n <= 16
    return bytes([0x51 + n - 1])


def addr2bytes(s):
    digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    n = 0
    for c in s:
        n *= 58
        if c not in digits58:
            raise ValueError
        n += digits58.index(c)
    h = '%x' % n
    if len(h) % 2:
        h = '0' + h
    for c in s:
        if c == digits58[0]:
            h = '00' + h
        else:
            break
    return unhexstr(h)[1:-4]  # skip version and checksum


def checkmultisig_scriptPubKey_dump(fd):
    data = fd.read(65 * 3)
    if not data:
        return None
    r = pushint(1)
    n = 0
    while data:
        chunk = data[0:65]
        data = data[65:]
        if len(chunk) < 33:
            chunk += b'\x00' * (33 - len(chunk))
        elif len(chunk) < 65:
            chunk += b'\x00' * (65 - len(chunk))
        r += pushdata(chunk)
        n += 1
    r += pushint(n) + OP_CHECKMULTISIG
    return r


def store_data_in_utxo(jsonrpc, input_data):
    uncompressed_file_size_in_bytes = sys.getsizeof(input_data)
    # print('Now storing preparing file for storage in blockchain. Original uncompressed file size in bytes: ' + str(
    #     uncompressed_file_size_in_bytes) + ' bytes')

    input_data_hash = get_digest(input_data)

    # TODO: remove unnecessary hashes
    compression_dictionary_file_hash = input_data_hash
    uncompressed_data_file_hash = input_data_hash
    compressed_data_file_hash = input_data_hash

    unspent = list(jsonrpc.listunspent())
    # TODO: figure out what this number should be
    (txins, change) = select_txins(1, unspent)
    txouts = []
    encoded_zstd_compressed_data = hexlify(input_data)
    length_of_compressed_data_string = '{0:015}'.format(len(encoded_zstd_compressed_data)).encode('utf-8')
    combined_data_hex = hexlify(length_of_compressed_data_string) + hexlify(compression_dictionary_file_hash) + hexlify(
        uncompressed_data_file_hash) + hexlify(
        compressed_data_file_hash) + encoded_zstd_compressed_data + hexlify(('0' * 100).encode('utf-8'))
    fd = io.BytesIO(combined_data_hex)
    while True:
        scriptPubKey = checkmultisig_scriptPubKey_dump(fd)
        if scriptPubKey is None:
            break
        value = Decimal(1000 / COIN)
        txouts.append((value, scriptPubKey))
        change -= value
    out_value = Decimal(base_transaction_amount)  # dest output
    change -= out_value
    receiving_blockchain_address = jsonrpc.getnewaddress()
    txouts.append((out_value, OP_DUP + OP_HASH160 + pushdata(
        addr2bytes(receiving_blockchain_address)) + OP_EQUALVERIFY + OP_CHECKSIG))
    change_address = jsonrpc.getnewaddress()  # change output
    txouts.append([change, OP_DUP + OP_HASH160 + pushdata(addr2bytes(change_address)) + OP_EQUALVERIFY + OP_CHECKSIG])
    tx = packtx(txins, txouts)
    signed_tx = jsonrpc.signrawtransaction(hexlify(tx).decode('utf-8'))
    fee = Decimal(len(signed_tx['hex']) / 1000) * FEEPERKB
    change -= fee
    txouts[-1][0] = change
    final_tx = packtx(txins, txouts)
    signed_tx = jsonrpc.signrawtransaction(hexlify(final_tx).decode('utf-8'))
    assert signed_tx['complete']
    hex_signed_transaction = signed_tx['hex']
    print("HEX SIGNED TRANSACTION", hex_signed_transaction)
    # print('Sending data transaction to address: ' + receiving_blockchain_address)
    # print('Size: %d  Fee: %2.8f' % (len(hex_signed_transaction) / 2, fee), file=sys.stderr)
    send_raw_transaction_result = jsonrpc.sendrawtransaction(hex_signed_transaction)
    blockchain_transaction_id = send_raw_transaction_result
    # print('Transaction ID: ' + blockchain_transaction_id)
    return blockchain_transaction_id


def retrieve_data_from_utxo(jsonrpc, blockchain_transaction_id):
    raw = jsonrpc.getrawtransaction(blockchain_transaction_id)
    outputs = raw.split('0100000000000000')
    # for idx, output in enumerate(outputs):
    #     print(idx, output)
    encoded_hex_data = ''
    for output in outputs[1:-2]:  # there are 3 65-byte parts in this that we need
        cur = 6
        encoded_hex_data += output[cur:cur + 130]
        cur += 132
        encoded_hex_data += output[cur:cur + 130]
        cur += 132
        encoded_hex_data += output[cur:cur + 130]
    encoded_hex_data += outputs[-2][6:-4]
    reconstructed_combined_data = binascii.a2b_hex(encoded_hex_data).decode('utf-8')
    reconstructed_length_of_compressed_data_hex_string = reconstructed_combined_data[
                                                         0:30]  # len(hexlify('{0:015}'.format(len(encoded_zstd_compressed_data)).encode('utf-8'))) is 30
    reconstructed_length_of_compressed_data_hex_string = int(
        unhexstr(reconstructed_length_of_compressed_data_hex_string).decode('utf-8').lstrip('0'))
    reconstructed_combined_data__remainder_1 = reconstructed_combined_data[30:]
    length_of_standard_hash_string = NetWorkSettings.HEX_DIGEST_SIZE
    reconstructed_compression_dictionary_file_hash = reconstructed_combined_data__remainder_1[
                                                     0:length_of_standard_hash_string]
    reconstructed_combined_data__remainder_2 = reconstructed_combined_data__remainder_1[length_of_standard_hash_string:]
    reconstructed_uncompressed_data_file_hash = reconstructed_combined_data__remainder_2[
                                                0:length_of_standard_hash_string]
    reconstructed_combined_data__remainder_3 = reconstructed_combined_data__remainder_2[length_of_standard_hash_string:]
    input_data_hash = reconstructed_combined_data__remainder_3[0:length_of_standard_hash_string]
    reconstructed_combined_data__remainder_4 = reconstructed_combined_data__remainder_3[length_of_standard_hash_string:]
    reconstructed_encoded_zstd_compressed_data_padded = reconstructed_combined_data__remainder_4.replace('A',
                                                                                                                   '')  # Note sure where this comes from; somehow it is introduced into the data (note this is "A" not "a").
    calculated_padding_length = len(
        reconstructed_encoded_zstd_compressed_data_padded) - reconstructed_length_of_compressed_data_hex_string
    reconstructed_encoded_zstd_compressed_data = reconstructed_encoded_zstd_compressed_data_padded[
                                                           0:-calculated_padding_length]
    output_data = unhexstr(reconstructed_encoded_zstd_compressed_data)
    hash_of_output_data = get_hexdigest(output_data)
    assert (hash_of_output_data == input_data_hash)
    # print('Successfully reconstructed and decompressed data!')
    return output_data
