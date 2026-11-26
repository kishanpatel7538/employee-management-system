import os

from app import create_app, db
from app.models import User, Employee

app = create_app()

if __name__ == "__main__":

    with app.app_context():

        try:
            db.create_all()

            print("Database connected successfully!")
            print("Users and Employees tables created!")

        except Exception as e:
            print("Database error:", e)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
