"""
SNMP Query model for storing query results.
"""
from datetime import datetime
from app.models import db


class SnmpQuery(db.Model):
    """Store SNMP query results for persistence."""
    
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(255), nullable=False)
    oid = db.Column(db.String(255), nullable=False)
    result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<SnmpQuery {self.host}:{self.oid} = {self.result}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'host': self.host,
            'oid': self.oid,
            'result': self.result,
            'timestamp': self.timestamp.isoformat()
        }
