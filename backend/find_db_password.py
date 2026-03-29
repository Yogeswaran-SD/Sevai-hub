#!/usr/bin/env python
"""Test different PostgreSQL password combinations."""

import psycopg2
from psycopg2 import OperationalError

db_configs = [
    # (user, password, description)
    ("postgres", "", "Empty password (default)"),
    ("postgres", "postgres", "Common default 'postgres'"),
    ("postgres", "password", "Common 'password'"),
    ("postgres", "postgres_dev_password_123", "From .env file"),
    ("root", "", "root user, empty password"),
    ("postgres", None, "No password parameter"),
]

print("=" * 70)
print("Testing PostgreSQL Connection Credentials")
print("=" * 70)

found_password = None

for user, password, desc in db_configs:
    try:
        if password is None:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user=user,
            )
        else:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user=user,
                password=password,
            )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        conn.close()
        
        print(f"\n✓ SUCCESS: {desc}")
        print(f"  User: {user}")
        print(f"  Password: {password if password else '(empty/no password)'}")
        print(f"  Version: {result[0][:50]}...")
        found_password = (user, password)
        break
        
    except OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            print(f"✗ {desc} - Password authentication failed")
        elif "fe_sendauth" in error_msg:
            print(f"✗ {desc} - Password required but empty")
        elif "server closed the connection" in error_msg:
            print(f"✗ {desc} - Server refused connection")
        else:
            print(f"✗ {desc} - {error_msg[:60]}")
    except Exception as e:
        print(f"✗ {desc} - Error: {str(e)[:60]}")

print("\n" + "=" * 70)

if found_password:
    user, pwd = found_password
    if pwd:
        print(f"\n✅ FOUND WORKING CREDENTIALS:")
        print(f"   Username: {user}")
        print(f"   Password: {pwd}")
        connection_string = f"postgresql://{user}:{pwd}@localhost:5432/sevaihub"
        print(f"\nUse this DATABASE_URL in .env:")
        print(f"DATABASE_URL={connection_string}")
    else:
        print(f"\n✅ FOUND WORKING CREDENTIALS:")
        print(f"   Username: {user}")
        print(f"   Password: (empty/not required)")
        connection_string = f"postgresql://{user}@localhost:5432/sevaihub"
        print(f"\nUse this DATABASE_URL in .env:")
        print(f"DATABASE_URL={connection_string}")
else:
    print("\n❌ Could not find working PostgreSQL credentials")
    print("Please:")
    print("1. Install PostgreSQL if not already installed")
    print("2. Set a password for the 'postgres' user")
    print("3. Update DATABASE_URL in .env with correct credentials")

print("=" * 70)
