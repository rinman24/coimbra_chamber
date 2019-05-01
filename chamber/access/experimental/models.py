"""Module including all sql alchemy models for chamber database."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Example(Base):
    """Example definition."""

    ___tablename__ = 'Example'
    __table_args__ = {'schema': 'my_schema'}

    ExampleId = Column(Integer, primary_key=True)
    Field_1 = Column(String(250))
