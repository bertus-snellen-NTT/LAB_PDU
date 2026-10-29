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


@main.route('/query', methods=['GET', 'POST'])
def run_query():
    """Run an SNMP query on a configured host."""
    hosts = get_all_hosts()
    
    if request.method == 'POST':
        host_id = request.form.get('host_id')
        oid = request.form.get('oid')
        save = request.form.get('save') == 'on'
        
        if not host_id or not oid:
            flash('Host and OID are required', 'error')
            return redirect(url_for('main.run_query'))
        
        # Get the host details
        selected_host = None
        for host in hosts:
            if str(host.id) == host_id:
                selected_host = host
                break
        
        if not selected_host:
            flash('Selected host not found', 'error')
            return redirect(url_for('main.run_query'))
        
        try:
            result = snmpv3_get(selected_host.host, oid, selected_host.port, save=save)
            flash(f'Query successful: {oid} = {result}', 'success')
            return redirect(url_for('main.show_host_queries', host=selected_host.host))
        except Exception as e:
            flash(f'Query failed: {str(e)}', 'error')
    
    return render_template('run_query.html', hosts=hosts)
