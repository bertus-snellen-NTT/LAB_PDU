"""
SNMP Host model for storing host configurations.
"""
from app.models import db


class SnmpHost(db.Model):
    """Store SNMP host configurations."""
    
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(255), unique=True, nullable=False)
    port = db.Column(db.Integer, default=161)
    description = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<SnmpHost {self.host}:{self.port}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port,
            'description': self.description
        }
