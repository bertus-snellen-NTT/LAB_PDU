from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.example_service import get_welcome_message, get_about_info
from app.services.snmp_service import add_host, get_all_hosts, get_queries_by_host, snmpv3_get
from app.services.device_service import add_device, get_valid_racks, get_devices_by_rack

main = Blueprint('main', __name__)


@main.route('/')
def index():
    message = get_welcome_message()
    return render_template('index.html', message=message)


@main.route('/about')
def about():
    info = get_about_info()
    return render_template('about.html', info=info)


@main.route('/rack/<rack_name>')
def rack_detail(rack_name):
    """Show detailed view of a specific rack."""
    devices = get_devices_by_rack(rack_name)
    return render_template('rack_detail.html', rack_name=rack_name, devices=devices)


@main.route('/devices/add', methods=['GET', 'POST'])
def add_device():
    """Add a device to a rack."""
    valid_racks = get_valid_racks()
    
    if request.method == 'POST':
        name = request.form.get('name')
        rack_id = request.form.get('rack_id')
        rack_u = int(request.form.get('rack_u', 1))
        rack_u_height = int(request.form.get('rack_u_height', 1))
        image_url = request.form.get('image_url', '')
        description = request.form.get('description', '')
        
        try:
            add_device(name, rack_id, rack_u, rack_u_height, image_url, description)
            flash(f'Device "{name}" added to {rack_id} at U{rack_u} (height: {rack_u_height}U)', 'success')
            return redirect(url_for('main.add_device'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error adding device: {str(e)}', 'error')
    
    return render_template('add_device.html', valid_racks=valid_racks)


@main.route('/hosts')
def list_hosts():
    """List all SNMP hosts and their queries."""
    hosts = get_all_hosts()
    return render_template('hosts.html', hosts=hosts)


@main.route('/hosts/add', methods=['GET', 'POST'])
def add_snmp_host():
    """Add a new SNMP host."""
    if request.method == 'POST':
        host = request.form.get('host')
        port = int(request.form.get('port', 161))
        description = request.form.get('description', '')
        
        if not host:
            flash('Host is required', 'error')
            return redirect(url_for('main.add_snmp_host'))
        
        try:
            add_host(host, port, description)
            flash(f'Host {host} added successfully', 'success')
            return redirect(url_for('main.list_hosts'))
        except Exception as e:
            flash(f'Error adding host: {str(e)}', 'error')
    
    return render_template('add_host.html')


@main.route('/hosts/<host>/queries')
def show_host_queries(host):
    """Show queries for a specific host."""
    queries = get_queries_by_host(host)
    return render_template('host_queries.html', host=host, queries=queries)


@main.route('/test-snmp', methods=['GET', 'POST'])
def test_snmp():
    """Test SNMP queries on configured hosts with common APC OIDs."""
    hosts = get_all_hosts()
    
    # Common APC PowerNet MIB OIDs
    apc_oids = {
        # PDU System Information
        'PDU Name': '1.3.6.1.4.1.318.1.1.26.1.1.1.0',
        'PDU Model': '1.3.6.1.4.1.318.1.1.26.1.1.2.0',
        'PDU Serial Number': '1.3.6.1.4.1.318.1.1.26.1.1.3.0',
        'PDU Firmware': '1.3.6.1.4.1.318.1.1.26.1.1.4.0',
        'PDU Location': '1.3.6.1.4.1.318.1.1.26.1.1.5.0',
        
        # Overall PDU Status
        'Overall Status': '1.3.6.1.4.1.318.1.1.26.2.1.0',
        'Overall Alarm Status': '1.3.6.1.4.1.318.1.1.26.2.2.0',
        'Total Current': '1.3.6.1.4.1.318.1.1.26.4.1.1.0',
        'Total Power': '1.3.6.1.4.1.318.1.1.26.4.1.2.0',
        'Total Apparent Power': '1.3.6.1.4.1.318.1.1.26.4.1.3.0',
        
        # Input Phase Monitoring (3-phase)
        'Phase 1 Voltage': '1.3.6.1.4.1.318.1.1.26.6.2.1.1.1',
        'Phase 1 Current': '1.3.6.1.4.1.318.1.1.26.6.2.1.2.1',
        'Phase 1 Power': '1.3.6.1.4.1.318.1.1.26.6.2.1.3.1',
        'Phase 2 Voltage': '1.3.6.1.4.1.318.1.1.26.6.2.1.1.2',
        'Phase 2 Current': '1.3.6.1.4.1.318.1.1.26.6.2.1.2.2',
        'Phase 2 Power': '1.3.6.1.4.1.318.1.1.26.6.2.1.3.2',
        'Phase 3 Voltage': '1.3.6.1.4.1.318.1.1.26.6.2.1.1.3',
        'Phase 3 Current': '1.3.6.1.4.1.318.1.1.26.6.2.1.2.3',
        'Phase 3 Power': '1.3.6.1.4.1.318.1.1.26.6.2.1.3.3',
        
        # Outlet Monitoring (first 8 outlets as examples)
        'Outlet 1 Name': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.2.1',
        'Outlet 1 Status': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.5.1',
        'Outlet 1 Current': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.6.1',
        'Outlet 1 Power': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.8.1',
        'Outlet 2 Name': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.2.2',
        'Outlet 2 Status': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.5.2',
        'Outlet 2 Current': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.6.2',
        'Outlet 2 Power': '1.3.6.1.4.1.318.1.1.26.6.3.2.1.8.2',
        
        # Additional outlet OIDs (table-based, instance 5)
        'Outlet 5 Status': '1.3.6.1.4.1.318.1.1.26.9.2.4.1.5',
    }
    
    if request.method == 'POST':
        host_id = request.form.get('host_id')
        oid = request.form.get('oid')
        save = request.form.get('save') == 'on'
        debug = request.form.get('debug') == 'on'
        
        if not host_id or not oid:
            flash('Host and OID are required', 'error')
            return redirect(url_for('main.test_snmp'))
        
        # Get the host details
        selected_host = None
        for host in hosts:
            if str(host.id) == host_id:
                selected_host = host
                break
        
        if not selected_host:
            flash('Selected host not found', 'error')
            return redirect(url_for('main.test_snmp'))
        
        try:
            result = snmpv3_get(selected_host.host, oid, selected_host.port, save=save, debug=debug)
            if result == "[NO_SUCH_INSTANCE]":
                flash(f'Query returned no data: OID {oid} does not exist on {selected_host.host} (No Such Instance)', 'warning')
            elif result == "":
                flash(f'Query returned no data: OID {oid} on {selected_host.host} returned empty result', 'warning')
            else:
                if debug:
                    flash(f'Debug: Raw result = "{result}"', 'info')
                flash(f'Query successful: {oid} = {result}', 'success')
            return redirect(url_for('main.show_host_queries', host=selected_host.host))
        except Exception as e:
            flash(f'Query failed: {str(e)}', 'error')
    
    return render_template('test_snmp.html', hosts=hosts, apc_oids=apc_oids)
