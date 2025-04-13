from urllib.parse import quote_plus

# if either contain special characters must be encoded
username = 'my_username'
password = 'my_password'

escaped_username=quote_plus(username)
escaped_password=quote_plus(password)

print(escaped_password)