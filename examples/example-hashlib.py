import hashlib

# Create a SHA256 hash object
hash_object = hashlib.sha256()

# Update the hash object with the data (must be bytes)
hash_object.update(b"This is a test string.")

# Get the hexadecimal representation of the hash
hex_digest = hash_object.hexdigest()

print(f"SHA256 Hash: {hex_digest}")