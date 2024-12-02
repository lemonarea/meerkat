# first line: 34
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
