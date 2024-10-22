from sqlalchemy import Column, Integer, String, Text
from database import Base, engine


class CodeReview(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    code = Column(Text)
    review_comments = Column(Text)


Base.metadata.create_all(bind=engine)
