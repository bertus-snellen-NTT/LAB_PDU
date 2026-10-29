# LAB_PDU

A standard Flask web application.

## Project Structure

```
LAB_PDU/
├── app/
│   ├── __init__.py          # App factory
│   ├── routes.py            # Blueprints and routes (thin controllers)
│   ├── services/            # Business logic (separate functions)
│   │   ├── __init__.py
│   │   └── example_service.py
│   ├── static/
│   │   └── css/
│   │       └── style.css    # Basic styling
│   └── templates/
│       ├── base.html        # Base template (nav, footer)
│       ├── index.html       # Home page
│       └── about.html       # About page
├── run.py                   # Entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── tests/
    └── test_routes.py       # Route tests
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/bertus-snellen-NTT/LAB_PDU.git
cd LAB_PDU
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and fill in your sensitive data:

```bash
cp .env.example .env
# Edit .env with your actual values
```

## Running the Application

### Development server

```bash
python run.py
```

The app will be available at `http://127.0.0.1:5000`

## Testing

Run the test suite:

```bash
pytest tests/
```

## Configuration

The following environment variables are supported:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for session security | dev-secret-key-change-in-production |
| `DATABASE_URI` | Database connection URI | sqlite:///app.db |
| `SNMP_USER` | SNMP v3 username | - |
| `SNMP_AUTH_KEY` | SNMP v3 authentication key | - |
| `SNMP_PRIV_KEY` | SNMP v3 privacy key | - |
| `SNMP_AUTH_PROTOCOL` | SNMP v3 auth protocol | usmHMACSHAAuthProtocol |
| `SNMP_PRIV_PROTOCOL` | SNMP v3 privacy protocol | usmDESPrivProtocol |

**APC PDU OID Notes:**
- OID `1.3.6.1.4.1.318.1.1.26.9.2.4.1.5` = Outlet 5 Status - Part of APC PowerNet MIB's outlet monitoring table. The `9.2.4` is the outlet status table, `1` is the outlet index (outlet 5), and the final `5` represents the status value (on/off, alarm state).

**Available SNMP v3 protocols:**
- Auth: `usmHMACSHAAuthProtocol`, `usmNoAuthProtocol`
- Privacy: `usmDESPrivProtocol`, `usmNoPrivProtocol`, `usmAesCfb128Protocol` (if AES support is compiled in), `usmAesCfb192Protocol`, `usmAesCfb256Protocol`

## Adding Sensitive Data

**Important:** Never commit sensitive data to Git.

1. Add your sensitive values to `.env` (this file is in `.gitignore`)
2. Access them in your code via `os.getenv('VARIABLE_NAME')`
3. Add new environment variable examples to `.env.example`

## Project Maintenance

- Keep `README.md` updated with any structural or setup changes
- Update `requirements.txt` when adding new dependencies with `pip freeze > requirements.txt`
- Add tests in the `tests/` directory for new functionality
