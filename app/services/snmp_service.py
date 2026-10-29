"""
SNMP v3 service for executing SNMP queries.
"""
import os
from pysnmp.hlapi.v3arch import (
    UsmUserData,
    usmHMACSHAAuthProtocol,
    usmNoAuthProtocol,
    usmNoPrivProtocol,
    usmDESPrivProtocol,
    ContextData,
    ObjectType,
    ObjectIdentity
)
from pysnmp.hlapi.v3arch.asyncio import UdpTransportTarget, get_cmd as getCmd, SnmpEngine
from pysnmp.proto.rfc1905 import NoSuchInstance
from app.models import db
from app.models.snmp_query import SnmpQuery
from app.models.host import SnmpHost

# Try to import AES protocols (optional, may not be available)
try:
    from pysnmp.hlapi.v3arch import (
        usmAesCfb128Protocol,
        usmAesCfb192Protocol,
        usmAesCfb256Protocol
    )
    HAS_AES = True
except ImportError:
    HAS_AES = False
    usmAesCfb128Protocol = None
    usmAesCfb192Protocol = None
    usmAesCfb256Protocol = None


def get_snmpv3_engine():
    """Create and return an SNMP v3 engine with settings from environment."""
    snmp_user = os.getenv('SNMP_USER')
    snmp_auth_key = os.getenv('SNMP_AUTH_KEY')
    snmp_priv_key = os.getenv('SNMP_PRIV_KEY')
    snmp_auth_protocol = os.getenv('SNMP_AUTH_PROTOCOL', 'usmHMACSHAAuthProtocol')
    snmp_priv_protocol = os.getenv('SNMP_PRIV_PROTOCOL', 'usmDESPrivProtocol')
    
    # Map string protocol names to actual protocol objects
    auth_protocol_map = {
        'usmHMACSHAAuthProtocol': usmHMACSHAAuthProtocol,
        'usmNoAuthProtocol': usmNoAuthProtocol,
    }
    priv_protocol_map = {
        'usmDESPrivProtocol': usmDESPrivProtocol,
        'usmNoPrivProtocol': usmNoPrivProtocol,
    }
    
    # Add AES protocols if available
    if HAS_AES:
        priv_protocol_map.update({
            'usmAesCfb128Protocol': usmAesCfb128Protocol,
            'usmAesCfb192Protocol': usmAesCfb192Protocol,
            'usmAesCfb256Protocol': usmAesCfb256Protocol,
        })
    
    auth_protocol = auth_protocol_map.get(snmp_auth_protocol, usmHMACSHAAuthProtocol)
    priv_protocol = priv_protocol_map.get(snmp_priv_protocol)
    
    # Fall back to DES if no privacy protocol specified or if AES not available
    if priv_protocol is None:
        priv_protocol = usmDESPrivProtocol
        if snmp_priv_protocol and snmp_priv_protocol not in priv_protocol_map:
            raise ValueError(f"Privacy protocol '{snmp_priv_protocol}' is not available. Available: {list(priv_protocol_map.keys())}")
    
    return UsmUserData(
        userName=snmp_user,
        authKey=snmp_auth_key,
        privKey=snmp_priv_key,
        authProtocol=auth_protocol,
        privProtocol=priv_protocol
    )


def snmpv3_get(host: str, oid: str, port: int = 161, save: bool = False, debug: bool = False) -> str:
    """
    Execute an SNMP v3 GET query.
    
    Args:
        host: SNMP target host
        oid: Object ID to query
        port: SNMP port (default: 161)
        save: Whether to save the query result to database (default: False)
        debug: Whether to print debug information (default: False)
    
    Returns:
        The value of the queried OID, or a special string for error conditions
    
    Raises:
        Exception: If SNMP query fails
    """
    import asyncio
    
    user_data = get_snmpv3_engine()
    transport = asyncio.run(UdpTransportTarget.create((host, port)))
    
    error_indication, error_status, error_index, var_binds = asyncio.run(
        getCmd(
            SnmpEngine(),
            user_data,
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
    )
    
    if error_indication:
        raise Exception(f"SNMP error: {error_indication}")
    
    if error_status:
        raise Exception(f"SNMP error: {error_status.prettyPrint()}")
    
    # Check for NoSuchInstance in var_binds
    for var_bind in var_binds:
        if debug:
            print(f"DEBUG: var_bind = {var_bind}")
            print(f"DEBUG: var_bind[0] = {var_bind[0]}")
            print(f"DEBUG: var_bind[1] = {var_bind[1]}")
            print(f"DEBUG: result type = {type(var_bind[1])}")
            print(f"DEBUG: result repr = {repr(var_bind[1])}")
        
        # Check if this is a NoSuchInstance response
        if isinstance(var_bind[1], NoSuchInstance):
            if debug:
                print(f"DEBUG: NoSuchInstance detected for OID {oid}")
            return "[NO_SUCH_INSTANCE]"
    
    result = ""
    for var_bind in var_binds:
        result = str(var_bind[1])
    
    if save:
        # Find or create the host
        db_host = SnmpHost.query.filter_by(host=host).first()
        if not db_host:
            db_host = add_host(host, port)
        
        query = SnmpQuery(host_id=db_host.id, oid=oid, result=result)
        db.session.add(query)
        db.session.commit()
    
    return result


def get_saved_queries(limit: int = 100):
    """
    Get saved SNMP queries from database.
    
    Args:
        limit: Maximum number of queries to return (default: 100)
    
    Returns:
        List of SnmpQuery objects
    """
    return SnmpQuery.query.order_by(SnmpQuery.timestamp.desc()).limit(limit).all()


def add_host(host: str, port: int = 161, description: str = None) -> SnmpHost:
    """
    Add a new SNMP host to the database.
    
    Args:
        host: Hostname or IP address
        port: SNMP port (default: 161)
        description: Optional description
    
    Returns:
        The created SnmpHost object
    """
    new_host = SnmpHost(host=host, port=port, description=description)
    db.session.add(new_host)
    db.session.commit()
    return new_host


def get_all_hosts() -> list:
    """
    Get all SNMP hosts from database.
    
    Returns:
        List of SnmpHost objects
    """
    return SnmpHost.query.order_by(SnmpHost.host).all()


def get_host_by_id(host_id: int) -> SnmpHost:
    """
    Get a specific SNMP host by ID.
    
    Args:
        host_id: The host ID
    
    Returns:
        SnmpHost object or None
    """
    return SnmpHost.query.get(host_id)


def get_queries_by_host(host: str, limit: int = 100) -> list:
    """
    Get SNMP queries for a specific host.
    
    Args:
        host: The hostname or IP address
        limit: Maximum number of queries to return (default: 100)
    
    Returns:
        List of SnmpQuery objects
    """
    db_host = SnmpHost.query.filter_by(host=host).first()
    if db_host:
        return SnmpQuery.query.filter_by(host_id=db_host.id).order_by(SnmpQuery.timestamp.desc()).limit(limit).all()
    return []
