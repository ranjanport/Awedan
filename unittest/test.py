import bcrypt
password = "super secret password"
# Hash a password for the first time, with a randomly-generated salt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
# Check that an unhashed password matches one that has previously been
if bcrypt.checkpw(password.encode('utf-8'), hashed):
    print("It Matches!")
else:
    print("It Does not Match :(")