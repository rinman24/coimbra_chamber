"""Module including all sql alchemy models for the database."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship, backref
# from sqlalchemy.dialects.mysql import BIT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# metadata = Base.metadata


class Pool(Base):
    """Pool object definition."""

    # Metadata
    __tablename__ = 'Pools'
    __table_args__ = {'schema': 'experimental'}

    # Columns
    pool_id = Column('PoolId', Integer, primary_key=True)
    inner_diameter = Column('InnerDiameter', Numeric(4, 4), nullable=False)
    outer_diameter = Column('OuterDiameter', Numeric(4, 4), nullable=False)
    height = Column('Height', Numeric(4, 4), nullable=False)
    material = Column('Material', String(50), nullable=False)
    mass = Column('Mass', Numeric(7, 7), nullable=False)


class Setting(Base):
    """Setting object definition."""

    # Metadata
    __tablename__ = 'Settings'
    __table_args__ = {'schema': 'experimental'}

    # Columns
    setting_id = Column('SettingId', Integer, primary_key=True)
    duty = Column('Duty', Numeric(4, 1), nullable=False)
    pressure = Column('Pressure', Integer, nullable=False)
    temperature = Column('Temperature', Numeric(4, 1), nullable=False)
    time_step = Column('TimeStep', Numeric(4, 2), nullable=False)


class Test(Base):
    """Test object definition."""

    # Metadata
    __tablename__ = 'Tests'
    __table_args__ = {'schema': 'experimental'}

    # Columns
    test_id = Column('TestId', Integer, primary_key=True)
    author = Column('Author', String, nullable=False)
    date_time = Column('DateTime', DateTime, nullable=False)
    description = Column('Description', String, nullable=False)

    # Foreign keys
    pool_id = Column(
        'Pools_PoolId', Integer, ForeignKey('experimental.Pools.PoolId'),
        nullable=False)
    setting_id = Column(
        'Settings_SettingId', Integer, ForeignKey('experimental.Settings.SettingId'),
        nullable=False)

    # Relationships
    pool = relationship('Pool', backref=backref('Tests'), order_by=test_id)
    setting = relationship('Setting', backref=backref('Tests'), order_by=test_id)


class Observation(Base):
    """Observation object definition."""

    # Metadata
    __tablename__ = 'Observations'
    __table_args__ = {'schema': 'experimental'}

    # Columns
    observation_id = Column('ObservationId', Integer, primary_key=True)
    cap_man_ok = Column('CapManOk', Boolean, nullable=False)
    dew_point = Column('DewPoint', Numeric(5, 2), nullable=False)
    idx = Column('Idx', Integer, nullable=False)
    mass = Column('Mass', Numeric(7, 7), nullable=False)
    optidew_ok = Column('OptidewOk', Boolean, nullable=False)
    pow_out = Column('PowOut', Numeric(6, 4))
    pow_ref = Column('PowRef', Numeric(6, 4))
    pressure = Column('Pressure', Integer, nullable=False)

    # Foreign keys
    test_id = Column(
        'Tests_TestId', Integer, ForeignKey('experimental.Tests.TestId'),
        nullable=False)

    # Relationships
    test = relationship(
        'Test', backref=backref('Onservations'), order_by=observation_id)


class Temperature(Base):
    """Temperature object definition."""

    # Metadata
    __tablename__ = 'Temperatures'
    __table_args__ = {'schema': 'experimental'}

    # Columns
    temperature_id = Column('TemperatureId', Integer, primary_key=True)
    thermocouple_num = Column('ThermocoupleNum', Integer, nullable=False)
    temperature = Column('Temperature', Numeric(5, 2), nullable=False)

    # Foreign keys
    observation_id = Column(
        'Observations_ObservationId', Integer,
        ForeignKey('experimental.Observations.ObservationId'), nullable=False)

    # Relationships
    observation = relationship(
        'Observation', backref=backref('Temperatures'), order_by=temperature_id)
