#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test bcrypt password hashing
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test passwords
test_passwords = [
    "password123",
    "Pass123!",
    "testpass123",
    "短いパス",
    "a" * 72,  # Max bcrypt length
    "a" * 100  # Over max length
]

print("Testing bcrypt password hashing...\n")

for password in test_passwords:
    try:
        print(f"Password: '{password}' (length: {len(password)}, bytes: {len(password.encode('utf-8'))})")
        hashed = pwd_context.hash(password)
        print(f"  ✓ Hashed successfully: {hashed[:60]}...")

        # Verify
        verified = pwd_context.verify(password, hashed)
        print(f"  ✓ Verification: {verified}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    print()
