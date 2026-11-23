from sqlmodel import Field, SQLModel, create_engine, Session

class Filedb(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    file_rg: str

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    user_type: str
    token: str
    user_id: str
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():  
    SQLModel.metadata.create_all(engine)
 
def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    create_db_and_tables()
