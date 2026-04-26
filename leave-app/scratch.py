import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

h = hash_password("stu123")
print("Hashed:", h)
print("Check:", check_password("stu123", h))
