"""
Database models for the application.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models to register them with SQLAlchemy
from app.models.snmp_query import SnmpQuery
from app.models.host import SnmpHost
from app.models.device import Device
