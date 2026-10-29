from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.example_service import get_welcome_message, get_about_info
from app.services.snmp_service import add_host, get_all_hosts, get_queries_by_host, snmpv3_get

main = Blueprint('main', __name__)


@main.route('/')
def index():
    message = get_welcome_message()
    return render_template('index.html', message=message)


@main.route('/about')
def about():
    info = get_about_info()
    return render_template('about.html', info=info)


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
        'System Description': '1.3.6.1.4.1.318.1.1.1.1.1.1.0',
        'System Name': '1.3.6.1.4.1.318.1.1.1.1.2.1.0',
        'System Contact': '1.3.6.1.4.1.318.1.1.1.1.3.1.0',
        'System Location': '1.3.6.1.4.1.318.1.1.1.1.4.1.0',
        'System Uptime': '1.3.6.1.2.1.1.3.0',
        'Input Voltage': '1.3.6.1.4.1.318.1.1.8.2.3.1.0',
        'Input Frequency': '1.3.6.1.4.1.318.1.1.8.2.4.1.0',
        'Input Current': '1.3.6.1.4.1.318.1.1.8.2.5.1.0',
        'Battery Status': '1.3.6.1.4.1.318.1.1.1.2.1.1.0',
        'Battery Temperature': '1.3.6.1.4.1.318.1.1.1.2.2.1.0',
        'Output Load': '1.3.6.1.4.1.318.1.1.4.2.2.1.0',
        'Output Voltage': '1.3.6.1.4.1.318.1.1.4.2.3.1.0',
        'Output Frequency': '1.3.6.1.4.1.318.1.1.4.2.4.1.0',
        'Output Current': '1.3.6.1.4.1.318.1.1.4.2.5.1.0',
        'Alarm Status': '1.3.6.1.4.1.318.1.1.1.1.5.1.0',
        'Firmware Version': '1.3.6.1.4.1.318.1.1.1.1.6.1.0',
        'Model Number': '1.3.6.1.4.1.318.1.1.1.1.7.1.0',
        'Serial Number': '1.3.6.1.4.1.318.1.1.1.1.8.1.0',
        'Manufacturer': '1.3.6.1.4.1.318.1.1.1.1.9.1.0',
    }
    
    if request.method == 'POST':
        host_id = request.form.get('host_id')
        oid = request.form.get('oid')
        save = request.form.get('save') == 'on'
        
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
            result = snmpv3_get(selected_host.host, oid, selected_host.port, save=save)
            flash(f'Query successful: {oid} = {result}', 'success')
            return redirect(url_for('main.show_host_queries', host=selected_host.host))
        except Exception as e:
            flash(f'Query failed: {str(e)}', 'error')
    
    return render_template('test_snmp.html', hosts=hosts, apc_oids=apc_oids)
