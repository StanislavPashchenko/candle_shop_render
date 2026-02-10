import sys
import os
try:
    import psycopg
    conn = psycopg.connect(host='localhost', user='postgres', password='linaga123', dbname='candle_shop', port=5432)
    cur = conn.cursor()
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    rows = cur.fetchall()
    print('\n'.join(r[0] for r in rows))
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
    sys.exit(1)
