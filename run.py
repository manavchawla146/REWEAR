from PetPocket import create_app, db
from PetPocket.models import User

# Create app context
app = create_app()
# with app.app_context():
#     # Force recreate all tables
#     db.drop_all()
#     db.create_all()

#     # Add a user within the same context
#     user = User(username="thor", email="thor@gmail.com", password_hash="thor")
#     db.session.add(user)
#     db.session.commit()
    
#     # Verify it was added
#     users = User.query.all()
#     print(users)

if __name__ == "__main__":
    app.run(debug=True)