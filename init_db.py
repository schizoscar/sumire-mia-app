# init_db.py
from app import create_app
from app.extensions import db

print("Creating database tables...")
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")
    
    # List all tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
