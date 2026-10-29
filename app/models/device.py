"""
Device model for storing devices in racks.
"""
from app.models import db


class Device(db.Model):
    """Store devices installed in racks."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    rack_id = db.Column(db.String(10), nullable=False)  # e.g., R1C1, R2C3
    rack_u = db.Column(db.Integer, nullable=False)  # Starting U position (1-42, bottom-up)
    rack_u_height = db.Column(db.Integer, default=1, nullable=False)  # Height in U
    image_url = db.Column(db.String(500))  # URL or path to device image
    description = db.Column(db.String(500))
    
    def __repr__(self):
        return f'<Device {self.name} in {self.rack_id} at U{self.rack_u}-U{self.rack_u + self.rack_u_height - 1}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'rack_id': self.rack_id,
            'rack_u': self.rack_u,
            'rack_u_height': self.rack_u_height,
            'rack_u_end': self.rack_u + self.rack_u_height - 1,
            'image_url': self.image_url,
            'description': self.description
        }
    
    @property
    def u_range(self):
        """Return U range as string (e.g., 'U5-U7')."""
        if self.rack_u_height == 1:
            return f"U{self.rack_u}"
        return f"U{self.rack_u}-U{self.rack_u + self.rack_u_height - 1}"
