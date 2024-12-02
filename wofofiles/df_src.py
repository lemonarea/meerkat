# Python libraries
import os
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text
from joblib import Memory
import datetime as dt

# Local imports
from wofofiles.conn import username, password, host, port, database


# Set up a directory for the cache
cache_dir = './cache'
memory = Memory(cache_dir, verbose=0)

# Define the caching function with expiration
def cache_with_expiry(func, expiry_minutes=10):
    def wrapper(*args, **kwargs):
        current_time = datetime.now()
        cache_file = os.path.join(cache_dir, func.__name__)
        if os.path.exists(cache_file):
            cache_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if (current_time - cache_time) < timedelta(minutes=expiry_minutes):
                return memory.cache(func)(*args, **kwargs)
            else:
                # Clear the old cache if expired
                memory.clear()
        return memory.cache(func)(*args, **kwargs)
    return wrapper

# Use your existing function but with caching
@cache_with_expiry
def dataset():
    query = """
    SELECT * FROM ownership

    """

    # Create the connection string and engine
    connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    engine = create_engine(connection_string)
    
    # Execute the query and return the DataFrame
    with engine.connect() as connection:
        df = pd.read_sql(text(query), connection)
    return df

# Now calling the function will use the cache if available and not expired
df = dataset()




