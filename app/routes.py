from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.example_service import get_welcome_message, get_about_info
from app.services.snmp_service import add_host, get_all_hosts, get_queries_by_host

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
