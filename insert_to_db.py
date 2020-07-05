from sqlalchemy import create_engine
def to_db(table,data):
	engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}?charset=utf8mb4"
                       .format(user="root",
                               pw="mtfbwy",
                               db="tripresso"))


	data.to_sql(table, con=engine,if_exists='append',chunksize = 1000, index= False)