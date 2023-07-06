import hashlib

SALT = "325 32rfewr3wqrf322###%Wa4"


def hash_password(password: str):
    password = f"{password}{SALT}"
    password = password.encode()
    return hashlib.md5(password).hexdigest()

def check_password(hash_pass, entry_pass):
    return hash_pass == entry_pass

# import hashlib

# salt = "534 jdncjdsnckrfrgtjsnc"

# def hash_password(password:str, salt: str):
# return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

# def check_password(hashed_password, user_password):
# password, salt = hashed_password.split(':')
# return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

# if __name__ == "__main__":
# # print(hash_password('text', salt))
# print(check_password(hash_password('text', salt), 'text'))