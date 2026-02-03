import yaml
import os
import bcrypt
from typing import List, Dict, Optional

class UserManager:
    def __init__(self, config_path="config/users.yaml"):
        self.config_path = config_path
        self._ensure_config_exists()
        self.users = self._load_users()

    def _ensure_config_exists(self):
        """Creates an empty users file if it doesn't exist."""
        if not os.path.exists(self.config_path):
            # Create directory if needed
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Default Admin
            default_users = {
                "users": [
                    {
                        "username": "admin",
                        "name": "Administrator",
                        "password_hash": "$2b$12$BY/gujZPEN5.p3P/8cVzh.ix59k1r3phehsthx/QQcYBwYN8HgvSK", # "admin"
                        "role": "admin"
                    }
                ]
            }
            self._save_users_to_file(default_users)

    def _load_users(self) -> List[Dict]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                users = data.get('users', [])
                
                # Check for plain text passwords and heal them
                modified = False
                for user in users:
                    pwd = user.get('password_hash', '')
                    # Bcrypt hashes typically start with $2a$ or $2b$
                    if pwd and not pwd.startswith('$2b$') and not pwd.startswith('$2a$'):
                        print(f"⚠️ Detected plain text password for user '{user['username']}'. Auto-hashing...")
                        user['password_hash'] = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
                        modified = True
                
                if modified:
                    self._save_users_to_file({"users": users})
                    print("✅ Users config updated with hashed passwords.")
                    
                return users
        except Exception as e:
            print(f"Error loading users: {e}")
            return []

    def _save_users_to_file(self, data):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def get_all_users(self):
        return self.users

    def get_user(self, username):
        for user in self.users:
            if user['username'] == username:
                return user
        return None

    def add_user(self, username, name, password, role="operator"):
        if self.get_user(username):
            return False, "Username already exists."

        # Hash Password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        new_user = {
            "username": username,
            "name": name,
            "password_hash": hashed,
            "role": role
        }
        
        self.users.append(new_user)
        self.save()
        return True, "User added successfully."

    def delete_user(self, username):
        if username == 'admin':
            return False, "Cannot delete default admin."
            
        initial_count = len(self.users)
        self.users = [u for u in self.users if u['username'] != username]
        
        if len(self.users) < initial_count:
            self.save()
            return True, "User deleted."
        return False, "User not found."

    def update_password(self, username, new_password):
        for user in self.users:
            if user['username'] == username:
                user['password_hash'] = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                self.save()
                return True, "Password updated."
        return False, "User not found."

    def save(self):
        self._save_users_to_file({"users": self.users})

    # For Streamlit Authenticator Compatibility
    def get_credentials_dict(self):
        """
        Converts user list to the dictionary format required by streamlit-authenticator.
        """
        usernames = {}
        for user in self.users:
            usernames[user['username']] = {
                'name': user['name'],
                'password': user['password_hash'],
                'role': user['role']
            }
        
        return {'usernames': usernames}
