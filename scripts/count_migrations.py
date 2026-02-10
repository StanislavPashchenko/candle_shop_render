import sys
try:
    import psycopg
    conn = psycopg.connect(host='localhost', user='postgres', password='linaga123', dbname='candle_shop', port=5432)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM django_migrations;")
    print(cur.fetchone()[0])
    cur.close()
    conn.close()
except Exception as e:
    print('Error:', e)
    sys.exit(1)
