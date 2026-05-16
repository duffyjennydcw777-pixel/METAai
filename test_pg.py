"""Quick PostgreSQL connectivity test via SSH tunnel"""
import socket
import sys

# Step 1: Raw TCP check
print("[1] TCP connect to localhost:15432...")
try:
    s = socket.create_connection(("localhost", 15432), timeout=5)
    # Try to read the PostgreSQL greeting
    data = s.recv(1024)
    print(f"    RAW response: {data[:100]}")
    s.close()
    print("    ✓ TCP OK")
except Exception as e:
    print(f"    ✗ TCP FAIL: {e}")
    sys.exit(1)

# Step 2: Try psycopg2 if available
print("\n[2] psycopg2 connect...")
try:
    import psycopg2
    conn = psycopg2.connect(
        host="localhost",
        port=15432,
        dbname="iron055",
        user="iron055",
        password="iron055pass2026",
        connect_timeout=5
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(f"    ✓ {cur.fetchone()[0]}")
    cur.close()
    conn.close()
except ImportError:
    print("    psycopg2 not installed, trying asyncpg...")
    try:
        import asyncio
        import asyncpg
        async def test():
            conn = await asyncpg.connect(
                host="localhost", port=15432,
                database="iron055", user="iron055",
                password="iron055pass2026", timeout=5
            )
            v = await conn.fetchval("SELECT version()")
            print(f"    ✓ {v}")
            await conn.close()
        asyncio.run(test())
    except ImportError:
        print("    No pg driver available. Install: pip install psycopg2-binary")
except Exception as e:
    print(f"    ✗ PG FAIL: {e}")
