
import os

from app import create_app, db
import app.models

app = create_app()

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        print("Database connected successfully!")
        print("All application tables initialized!")
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
