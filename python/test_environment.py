
from config import get_connection

connection = get_connection(include_database=False)

if connection:
    connection.close()
    print("Environment test passed!")
