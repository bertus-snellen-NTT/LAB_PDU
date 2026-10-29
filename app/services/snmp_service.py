"""
SNMP v3 service for executing SNMP queries.
"""
import os
from pysnmp.hlapi import *


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


def snmpv3_get(host: str, oid: str, port: int = 161) -> str:
    """
    Execute an SNMP v3 GET query.
    
    Args:
        host: SNMP target host
        oid: Object ID to query
        port: SNMP port (default: 161)
    
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
    
    for var_bind in var_binds:
        return str(var_bind[1])
    
    return ""
