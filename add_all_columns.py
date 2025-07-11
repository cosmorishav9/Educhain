from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as connection:
        try:
            # Try adding 'email' to user table
            connection.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(120);'))
            print("✅ Email column added successfully!")
        except Exception as e:
            print(f"⚠️ Email column might already exist or failed: {e}")

        try:
            # Add new certificate fields
            connection.execute(text('ALTER TABLE certificate ADD COLUMN dob VARCHAR(100);'))
            connection.execute(text('ALTER TABLE certificate ADD COLUMN class_10_marks VARCHAR(20);'))
            connection.execute(text('ALTER TABLE certificate ADD COLUMN class_12_marks VARCHAR(20);'))
            connection.execute(text('ALTER TABLE certificate ADD COLUMN stream VARCHAR(100);'))
            connection.execute(text('ALTER TABLE certificate ADD COLUMN cgpa VARCHAR(10);'))
            print("✅ Certificate fields added successfully!")
        except Exception as e:
            print(f"⚠️ Certificate field addition failed or already exists: {e}")
