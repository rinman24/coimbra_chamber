"""Data models for experiment access."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    String,
    Text)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


# Mapped classes -------------------------------------------------------------


Base = declarative_base()
metadata = Base.metadata


class Tube(Base):
    """Tube object definition."""

    # Metadata
    __tablename__ = 'Tubes'

    # Columns
    tube_id = Column(Integer, primary_key=True)
    inner_diameter = Column(Numeric(4, 4), nullable=False)
    outer_diameter = Column(Numeric(4, 4), nullable=False)
    height = Column(Numeric(4, 4), nullable=False)
    material = Column(String(50), nullable=False)
    mass = Column(Numeric(7, 7), nullable=False)

    # Children relationships
    experiments = relationship('Experiment', back_populates='tube')

    def __repr__(self):  # noqa: D105
        return (
            f'<Tube(inner_diameter={self.inner_diameter}, '
            f'outer_diameter={self.outer_diameter}, '
            f'height={self.height}, '
            f"material='{self.material}', "
            f'mass={self.mass})>')


class Setting(Base):
    """Setting object definition."""

    # Metadata
    __tablename__ = 'Settings'

    # Columns
    setting_id = Column(Integer, primary_key=True)
    duty = Column(Numeric(4, 1), nullable=False)
    pressure = Column(Integer, nullable=False)
    temperature = Column(Numeric(4, 1), nullable=False)
    time_step = Column(Numeric(4, 2), nullable=False)

    # Children relationships
    experiments = relationship('Experiment', back_populates='setting')

    def __repr__(self):  # noqa: D105
        return (
            f'<Setting(duty={self.duty}, '
            f'pressure={self.pressure}, '
            f'temperature={self.temperature}, '
            f'time_step={self.time_step})>')


class Experiment(Base):
    """Experiment object definition."""

    # Metadata
    __tablename__ = 'Experiments'

    # Columns
    experiment_id = Column(Integer, primary_key=True)
    author = Column(String(10), nullable=False)
    datetime = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)

    # Foreign keys
    tube_id = Column(Integer, ForeignKey('Tubes.tube_id'))
    setting_id = Column(Integer, ForeignKey('Settings.setting_id'))

    # Parent relationships
    tube = relationship('Tube', back_populates='experiments')
    setting = relationship('Setting', back_populates='experiments')

    # Children relationships
    observations = relationship('Observation', back_populates='experiment')

    def __repr__(self):  # noqa: D105
        return (
            f"<Experiment(author='{self.author}', "
            f'datetime=datetime({self.datetime.year}, '
            f'{self.datetime.month}, '
            f'{self.datetime.hour}, '
            f'{self.datetime.minute}, '
            f'{self.datetime.second}, '
            f'{self.datetime.microsecond}), '
            f"description='{self.description[:20]}...')>")


class Observation(Base):
    """Observation object definition."""

    # Metadata
    __tablename__ = 'Observations'

    # Columns
    cap_man_ok = Column(Boolean, nullable=False)
    dew_point = Column(Numeric(5, 2), nullable=False)
    idx = Column(Integer, primary_key=True)
    mass = Column(Numeric(7, 7), nullable=False)
    optidew_ok = Column(Boolean, nullable=False)
    pow_out = Column(Numeric(6, 4))
    pow_ref = Column(Numeric(6, 4))
    pressure = Column(Integer, nullable=False)
    surface_temp = Column(Numeric(5, 2))

    # Foreign keys
    experiment_id = Column(
        Integer, ForeignKey('Experiments.experiment_id'),
        primary_key=True)

    # Parent relationship
    experiment = relationship('Experiment', back_populates='observations')

    def __repr__(self):  # noqa: D105
        return (
            f'<Observation(cap_man_ok={self.cap_man_ok}, '
            f'dew_point={self.dew_point}, '
            f'idx={self.idx}, '
            f'mass={self.mass}, '
            f'optidew_ok={self.optidew_ok}, '
            f'pow_out={self.pow_out}, '
            f'pow_ref={self.pow_ref}, '
            f'pressure={self.pressure})>')


class Temperature(Base):
    """Temperature object definition."""

    # Metadata
    __tablename__ = 'Temperatures'

    # Columns
    thermocouple_num = Column(Integer, primary_key=True)
    temperature = Column(Numeric(5, 2))

    # Composite foreign keys
    idx = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            [idx, experiment_id], [Observation.idx, Observation.experiment_id]),
        )

    def __repr__(self):  # noqa: D105
        return (
            f'<Temperature(thermocouple_num={self.thermocouple_num}, '
            f'temperature={self.temperature}, '
            f'idx={self.idx}, '
            f'experiment_id={self.experiment_id})>')
