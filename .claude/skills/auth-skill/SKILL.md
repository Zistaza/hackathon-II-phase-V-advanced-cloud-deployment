---
name: auth-skill
description: Handle user authentication operations securely, including signup, signin, password hashing, JWT token generation, and Better Auth integration.
---

# Auth Skill

## Instructions

1. **Signup flow**
   - Accept user credentials (email, password)
   - Hash the password securely using bcrypt or Argon2
   - Store user details in the database
   - Generate a JWT token upon successful signup
   - Integrate with Better Auth API for external authentication support

2. **Signin flow**
   - Accept user credentials (email, password)
   - Retrieve stored hashed password from database
   - Verify password using Auth Skill hash verification function
   - Generate and return a JWT token if authentication succeeds
   - Handle errors clearly for invalid credentials

3. **Password hashing**
   - Use bcrypt or Argon2 for strong password security
   - Ensure salts are unique per password
   - Provide functions to hash and verify passwords separately

4. **JWT token handling**
   - Generate JWT token with user_id and expiry claims
   - Validate tokens for protected routes
   - Return structured payload with token and metadata

5. **Better Auth integration**
   - Call Better Auth API for additional signup/signin verification
   - Handle responses and errors gracefully
   - Ensure consistency with internal token system

## Best Practices
- Never store plain-text passwords
- Use strong hashing algorithms
- Set JWT expiration and refresh mechanisms
- Validate all inputs before calling Auth Skill functions
- Ensure all responses are consistent and structured

## Example Structure
```python
class AuthSkill:
    def signup(self, email: str, password: str):
        hashed = self.hash_password(password)
        user_id = self.save_user(email, hashed)
        token = self.create_jwt_token(user_id)
        self.better_auth_signup(email)
        return {"user_id": user_id, "token": token}

    def signin(self, email: str, password: str):
        hashed = self.get_hashed_password(email)
        if self.verify_password(password, hashed):
            token = self.create_jwt_token(user_id=email)
            self.better_auth_signin(email)
            return {"token": token}
        return {"error": "Invalid credentials"}

    def hash_password(self, password: str) -> str:
        # bcrypt hashing logic
        pass

    def verify_password(self, password: str, hashed: str) -> bool:
        # bcrypt verification logic
        pass

    def create_jwt_token(self, user_id: int) -> str:
        # JWT generation logic
        pass

    def better_auth_signup(self, email: str):
        # Better Auth API signup integration
        pass

    def better_auth_signin(self, email: str):
        # Better Auth API signin integration
        pass