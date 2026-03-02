import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def test_connection():
    """Test PostgreSQL connection."""
    database_url = os.environ.get('DATABASE_URL')
    print(f"Connecting to: {database_url}")
    
    try:
        # Handle Render URL format
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Test query
        cur.execute('SELECT version()')
        version = cur.fetchone()
        print(f"✅ Connected successfully!")
        print(f"PostgreSQL version: {version[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == '__main__':
    test_connection()
