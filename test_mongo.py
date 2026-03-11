from dotenv import load_dotenv
load_dotenv()

from app.config import Config
Config.validate()
print('✓ Config validated')

from app.database.mongo_connection import get_mongo_client, close_mongo_connection
client = get_mongo_client()
print('✓ MongoDB connection successful')

from app.database.init_db import initialize_database
initialize_database()
print('✓ Database initialized')

close_mongo_connection()