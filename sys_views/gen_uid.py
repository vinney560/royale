import string, random

# Geneate string (16chars)
_id = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=30))
print(_id)