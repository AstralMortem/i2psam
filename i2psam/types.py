from enum import IntEnum, StrEnum


class CryptoKeyType(IntEnum):
    ELGAMAL = 0
    P256 = 1
    P384 = 2
    P521 = 3
    X25519 = 4
    MLKEM512_X25519 = 5
    MLKEM768_X25519 = 6
    MLKEM1024_X25519 = 7
    # 255 reserved (NONE), 65280+ experimental, 65535 future


class SigningKeyType(IntEnum):
    DSA_SHA1 = 0
    ECDSA_SHA256_P256 = 1
    ECDSA_SHA384_P384 = 2
    ECDSA_SHA512_P521 = 3
    RSA_SHA256_2048 = 4
    RSA_SHA384_3072 = 5
    RSA_SHA512_4096 = 6
    EDDSA_SHA512_ED25519 = 7
    EDDSA_SHA512_ED25519PH = 8
    # 9..10 reserved (GOST)
    REDDSA_SHA512_ED25519 = 11
    # 12..20 reserved (MLDSA), 65280+ experimental, 65535 future


class Result(StrEnum):
    OK = "OK"
    CANT_REACH_PEER = "CANT_REACH_PEER"
    DUPLICATED_DEST = "DUPLICATED_DEST"
    I2P_ERROR = "I2P_ERROR"
    INVALID_KEY = "INVALID_KEY"
    KEY_NOT_FOUND = "KEY_NOT_FOUND"
    PEER_NOT_FOUND = "PEER_NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    LEASESET_NOT_FOUND = "LEASESET_NOT_FOUND"


class SessionStyle(StrEnum):
    STREAM = "STREAM"
    DATAGRAM = "DATAGRAM"
    RAW = "RAW"
    DATAGRAM2 = "DATAGRAM2"
    DATAGRAM3 = "DATAGRAM3"
