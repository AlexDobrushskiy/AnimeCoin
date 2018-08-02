import random

def getrandbytes(n):
    return random.getrandbits(n * 8).to_bytes(n, byteorder="big")
