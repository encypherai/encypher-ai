from cryptography.hazmat.primitives.asymmetric import ed25519

# Generate a fixed demo key for development
key = ed25519.Ed25519PrivateKey.generate()
private_bytes = key.private_bytes_raw()
print(f"DEMO_PRIVATE_KEY_HEX={private_bytes.hex()}")
