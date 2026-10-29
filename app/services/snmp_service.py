"""
SNMP v3 service for executing SNMP queries.
"""
import os
from pysnmp.hlapi import *
from app.models import db
from app.models.snmp_query import SnmpQuery


def get_snmpv3_engine():
    """Create and return an SNMP v3 engine with settings from environment."""
    snmp_user = os.getenv('SNMP_USER')
    snmp_auth_key = os.getenv('SNMP_AUTH_KEY')
    snmp_priv_key = os.getenv('SNMP_PRIV_KEY')
    snmp_auth_protocol = os.getenv('SNMP_AUTH_PROTOCOL', 'usmHMACSHAAuthProtocol')
    snmp_priv_protocol = os.getenv('SNMP_PRIV_PROTOCOL', 'usmAesCfb128Protocol')
    
    return UsmUserData(
        userName=snmp_user,
        authKey=snmp_auth_key,
        privKey=snmp_priv_key,
        authProtocol=eval(snmp_auth_protocol),
        privProtocol=eval(snmp_priv_protocol)
    )


def snmpv3_get(host: str, oid: str, port: int = 161, save: bool = False) -> str:
    """
    Execute an SNMP v3 GET query.
    
    Args:
        host: SNMP target host
        oid: Object ID to query
        port: SNMP port (default: 161)
        save: Whether to save the query result to database (default: False)
    
    Returns:
        The value of the queried OID
    
    Raises:
        Exception: If SNMP query fails
    """
    user_data = get_snmpv3_engine()
    
    error_indication, error_status, error_index, var_binds = next(
        getCmd(
            SnmpEngine(),
            CommunityData('public'),  # Not used for v3, but required by API
            user_data,
            UdpTransportTarget((host, port)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
    )
    
    if error_indication:
        raise Exception(f"SNMP error: {error_indication}")
    
    if error_status:
        raise Exception(f"SNMP error: {error_status.prettyPrint()}")
    
    result = ""
    for var_bind in var_binds:
        result = str(var_bind[1])
    
    if save:
        query = SnmpQuery(host=host, oid=oid, result=result)
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
