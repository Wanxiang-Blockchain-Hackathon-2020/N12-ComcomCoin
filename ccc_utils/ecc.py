from py_ecc import bls
import random


def gen_priv_key(file=None):
    private_key = random.randint(19999999999999999999, 99999999999999999999)
    if file is not None:
        try:
            with open(file, 'w') as f:
                f.write(str(private_key))
        except PermissionError:
            return None
    return private_key


def gen_pub_key(private_key, file=None):
    public_key = bls.privtopub(private_key)

    if file is not None:
        try:
            with open(file, 'w') as f:
                f.write(str(int.from_bytes(public_key, byteorder='big', signed=False)))
        except PermissionError:
            return None
    return public_key


def sign(private_key, msg:bytes):
    try:
        private_key = int(private_key)
        message_hash = b'\xab' * 32
        signature = bls.sign(message_hash, private_key, msg)
        return signature
    except TypeError:
        return None


def verify_sign(public_key, signature, msg: bytes):
    try:
        message_hash = b'\xab' * 32
        return bls.verify(message_hash, public_key, signature, msg)
    except TypeError:
        return False


def get_priv_key(file):
    try:
        with open(file, 'r') as f:
            private_key = int(f.read())
            return private_key
    except FileNotFoundError:
        return None


def get_pub_key(file,format='bytes'):
    try:
        with open(file, 'r') as f:
            if format == 'bytes':
                public_key = int(f.read()).to_bytes(length=48, byteorder='big')
            else:
                public_key = f.read()
            return public_key
    except FileNotFoundError:
        return None

def pub_key_str_2_bytes(pub_key_str):
    return int(pub_key_str.strip()).to_bytes(length=48, byteorder='big')

def signature_str_2_bytes(pub_key_str):
    return int(pub_key_str.strip()).to_bytes(length=96,byteorder='big')

def init_keys():
    priv_key = gen_priv_key('priv_genesis.txt')
    pub_key = gen_pub_key(private_key=priv_key,file='pub_genesis.txt')

    priv_key = gen_priv_key('priv.txt')
    pub_key = gen_pub_key(private_key=priv_key, file='pub.txt')

    msg = 'str(pub_key)+":xxxxxx"'.encode('utf-8')
    signature = sign(priv_key, msg)
