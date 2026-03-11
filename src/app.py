"""
DevSecOps Portfolio Project 1 — Intentionally Vulnerable Flask App
WARNING: This code contains deliberate vulnerabilities for educational purposes.
DO NOT deploy to production. DO NOT use these patterns in real code.

Vulnerabilities included:
  - CWE-89:  SQL Injection
  - CWE-78:  Command Injection
  - CWE-79:  Cross-Site Scripting (XSS)
  - CWE-502: Insecure Deserialization
  - CWE-798: Hardcoded Credentials
  - CWE-94:  Debug Mode Enabled
"""

import subprocess
import pickle
import yaml
from flask import Flask, request, render_template_string
from sqlalchemy import create_engine, text

app = Flask(__name__)

# ── CWE-798: Hardcoded Credentials ──────────────────────────────
# These will be detected by Trufflehog (secret scanning)
DATABASE_PASSWORD = "SuperSecret123!"
API_KEY = "sk-prod-abc123xyz789secret"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# Database connection using hardcoded credentials
engine = create_engine(f"sqlite:///test.db")


@app.route("/user")
def get_user():
    """CWE-89: SQL Injection — user input concatenated directly into query."""
    username = request.args.get("name", "")
    # VULNERABLE: never concatenate user input into SQL
    query = f"SELECT * FROM users WHERE username = '{username}'"
    with engine.connect() as conn:
        result = conn.execute(text(query))
    return str(result.fetchall())


@app.route("/ping")
def ping():
    """CWE-78: Command Injection — user input passed to shell."""
    host = request.args.get("host", "localhost")
    # VULNERABLE: shell=True with user input allows arbitrary command execution
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True)
    return result.stdout.decode()


@app.route("/hello")
def hello():
    """CWE-79: Cross-Site Scripting — user input rendered without escaping."""
    name = request.args.get("name", "World")
    # VULNERABLE: render_template_string with user input allows XSS
    template = f"<h1>Hello {name}!</h1>"
    return render_template_string(template)


@app.route("/load", methods=["POST"])
def load_data():
    """CWE-502: Insecure Deserialization — pickle deserialises untrusted input."""
    data = request.get_data()
    # VULNERABLE: pickle.loads on untrusted data allows remote code execution
    obj = pickle.loads(data)
    return str(obj)


@app.route("/config")
def load_config():
    """CWE-502: Insecure YAML load — yaml.load with untrusted input."""
    config_data = request.args.get("config", "{}")
    # VULNERABLE: yaml.load without Loader allows code execution
    config = yaml.load(config_data)
    return str(config)


@app.route("/health")
def health():
    """Safe endpoint — used by Docker HEALTHCHECK."""
    return {"status": "ok"}, 200


if __name__ == "__main__":
    # CWE-94: Debug mode exposes interactive debugger to anyone who can reach the app
    # VULNERABLE: debug=True must never be used in production
    app.run(host="0.0.0.0", port=8080, debug=True)
