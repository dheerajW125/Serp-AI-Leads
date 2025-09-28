from sqlalchemy import create_engine, Column, Integer, String, Index
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = 'sqlite:///db.sqlite3'

engine = create_engine(DATABASE_URL, echo=False)

Base = declarative_base()

class ScrapedLink(Base):
    __tablename__ = 'scraped_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)

    __table_args__ = (
        Index('idx_scheme', 'url'),
    )

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def insert_link(url):
    session = Session()
    new_link = ScrapedLink(url=url)
    try:
        session.add(new_link)
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

def link_exists(url):
    session = Session()
    exists = session.query(ScrapedLink).filter_by(url=url).first() is not None
    session.close()
    return exists
