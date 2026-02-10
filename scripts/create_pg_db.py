import sys
import os

def main():
    if len(sys.argv) != 6:
        print("Usage: create_pg_db.py dbname dbuser dbpassword host port")
        sys.exit(2)
    dbname, dbuser, dbpassword, host, port = sys.argv[1:]
    try:
        try:
            import psycopg
            conn = psycopg.connect(host=host, user=dbuser, password=dbpassword, dbname='postgres', port=port)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE {dbname}")
                print(f"Database '{dbname}' created.")
            else:
                print(f"Database '{dbname}' already exists.")
            cur.close()
            conn.close()
        except ImportError:
            import psycopg2
            conn = psycopg2.connect(host=host, user=dbuser, password=dbpassword, dbname='postgres', port=port)
            conn.set_session(autocommit=True)
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (dbname,))
            exists = cur.fetchone()
            if not exists:
                cur.execute(f"CREATE DATABASE {dbname}")
                print(f"Database '{dbname}' created.")
            else:
                print(f"Database '{dbname}' already exists.")
            cur.close()
            conn.close()
    except Exception as e:
        print("Error creating database:", e)
        sys.exit(1)

if __name__ == '__main__':
    main()
