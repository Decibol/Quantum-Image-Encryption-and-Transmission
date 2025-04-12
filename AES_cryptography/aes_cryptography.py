import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import numpy as np

def encrypt_image(image_bytes, key_bits):
    """Encrypts the image using AES-CBC."""
    key_bytes = bytes([int(''.join(map(str, key_bits[i:i+8])), 2) for i in range(0, 128, 8)])
    
    # Pad image bytes
    padder = padding.PKCS7(128).padder()
    padded_image = padder.update(image_bytes) + padder.finalize()
    
    # Generate IV
    iv = os.urandom(16)
    
    # AES Encryption
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_image) + encryptor.finalize()
    
    return iv, ciphertext

def decrypt_image(ciphertext, iv, key_bits, img_shape):
    """Decrypts the image using AES-CBC, handling potential decryption errors."""
    # Convert key bits (list of 0s and 1s) to bytes (128 bits = 16 bytes)
    key_bytes = bytes([int(''.join(map(str, key_bits[i:i+8])), 2) for i in range(0, 128, 8)])
    
    # Set up AES-CBC decryption
    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    try:
        # Attempt to unpad the decrypted data
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_image_bytes = unpadder.update(decrypted_padded) + unpadder.finalize()
    except ValueError:
        # If unpadding fails due to invalid padding (e.g., wrong key), use padded bytes
        decrypted_image_bytes = decrypted_padded
    
    # Calculate expected number of bytes for the image
    expected_bytes = np.prod(img_shape)
    
    # Adjust byte length to match image shape
    if len(decrypted_image_bytes) > expected_bytes:
        decrypted_image_bytes = decrypted_image_bytes[:expected_bytes]  # Truncate excess
    elif len(decrypted_image_bytes) < expected_bytes:
        decrypted_image_bytes += b'\x00' * (expected_bytes - len(decrypted_image_bytes))  # Pad with zeros
    
    # Convert bytes to numpy array and reshape to original image dimensions
    return np.frombuffer(decrypted_image_bytes, dtype=np.uint8).reshape(img_shape)