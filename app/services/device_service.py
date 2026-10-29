"""
Device service for managing devices in racks.
"""
from app.models import db
from app.models.device import Device

# Valid racks that accept devices
VALID_RACKS = ['R1C1', 'R1C2', 'R1C3', 'R2C1', 'R2C2', 'R2C3']


def add_device(name: str, rack_id: str, rack_u: int, rack_u_height: int = 1, image_url: str = None, description: str = None) -> Device:
    """
    Add a new device to the database.
    
    Args:
        name: Device name
        rack_id: Rack identifier (e.g., R1C1)
        rack_u: Starting U position (1-42, bottom-up)
        rack_u_height: Height in U (default: 1)
        image_url: URL to device image
        description: Optional description
    
    Returns:
        The created Device object
    
    Raises:
        ValueError: If rack_id is invalid or U position is out of range
    """
    if rack_id not in VALID_RACKS:
        raise ValueError(f"Invalid rack: {rack_id}. Valid racks: {', '.join(VALID_RACKS)}")
    
    if rack_u < 1 or rack_u > 42:
        raise ValueError(f"U position must be between 1 and 42, got {rack_u}")
    
    if rack_u_height < 1:
        raise ValueError(f"U height must be at least 1, got {rack_u_height}")
    
    # Check if the U space is already occupied
    end_u = rack_u + rack_u_height - 1
    if end_u > 42:
        raise ValueError(f"Device exceeds rack height. Ends at U{end_u}, max is U42")
    
    existing = Device.query.filter(
        Device.rack_id == rack_id,
        Device.rack_u <= end_u,
        Device.rack_u + Device.rack_u_height - 1 >= rack_u
    ).first()
    
    if existing:
        raise ValueError(f"U space {rack_u}-{end_u} in {rack_id} is already occupied by {existing.name}")
    
    new_device = Device(
        name=name,
        rack_id=rack_id,
        rack_u=rack_u,
        rack_u_height=rack_u_height,
        image_url=image_url,
        description=description
    )
    db.session.add(new_device)
    db.session.commit()
    return new_device


def get_devices_by_rack(rack_id: str) -> list:
    """
    Get all devices in a specific rack.
    
    Args:
        rack_id: Rack identifier
    
    Returns:
        List of Device objects
    """
    return Device.query.filter_by(rack_id=rack_id).order_by(Device.rack_u).all()


def get_all_devices() -> list:
    """
    Get all devices from the database.
    
    Returns:
        List of Device objects
    """
    return Device.query.order_by(Device.rack_id, Device.rack_u).all()


def get_device_by_id(device_id: int) -> Device:
    """
    Get a specific device by ID.
    
    Args:
        device_id: The device ID
    
    Returns:
        Device object or None
    """
    return Device.query.get(device_id)


def delete_device(device_id: int) -> bool:
    """
    Delete a device from the database.
    
    Args:
        device_id: The device ID
    
    Returns:
        True if deleted, False if not found
    """
    device = Device.query.get(device_id)
    if device:
        db.session.delete(device)
        db.session.commit()
        return True
    return False


def get_valid_racks() -> list:
    """
    Get list of valid racks for device placement.
    
    Returns:
        List of valid rack IDs
    """
    return VALID_RACKS.copy()
