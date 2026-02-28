import asyncio
import asyncpg
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

async def test_conn():
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    database = os.getenv('DB_NAME')
    host = "17.72.93.24"
    port = os.getenv('DB_PORT')
    
    print(f"Connecting to {host}:{port} as {user}...")
    
    print("--- Trying without SSL ---")
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port
        )
        print("Connected successfully without SSL!")
        await conn.close()
    except Exception as e:
        print(f"Failed without SSL: {e}")
        
    print("\n--- Trying with SSL (ssl=True) ---")
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
            ssl=True
        )
        print("Connected successfully with SSL (ssl=True)!")
        await conn.close()
    except Exception as e:
        print(f"Failed with SSL (ssl=True): {e}")

    print("\n--- Trying with SSL (ssl='require' equivalent) ---")
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        conn = await asyncpg.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
            ssl=ctx
        )
        print("Connected successfully with SSL (custom context)!")
        await conn.close()
    except Exception as e:
        print(f"Failed with SSL (custom context): {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
