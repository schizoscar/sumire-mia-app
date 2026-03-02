from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # Check if user exists
    if not User.query.filter_by(username='test').first():
        user = User(
            username='test',
            email='test@example.com',
            color_scheme='purple',
            is_admin=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print("✅ Test user created!")
        print("   Username: test")
        print("   Password: password123")
    else:
        print("✅ Test user already exists")
