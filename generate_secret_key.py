#!/usr/bin/env python
"""
Generate a secure Django secret key
"""
import secrets
import string

# Generate a secure random secret key
chars = string.ascii_letters + string.digits + string.punctuation
secret_key = ''.join(secrets.choice(chars) for _ in range(50))

print("Generated Django SECRET_KEY:")
print(secret_key)
print("\nAdd this to your .env file like this:")
print(f"SECRET_KEY='{secret_key}'")
