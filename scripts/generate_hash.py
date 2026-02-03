import bcrypt
import sys

def generate_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        password = "admin"
    
    hashed = generate_hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
