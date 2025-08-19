def print_section(title):

# OSINT Tool Starter - Advanced Workflow
# Author: (your name)
# Description: Modular, extensible OSINT tool for domains


# All imports and code blocks are now properly indented and structured
import argparse
import socket
import dns.resolver
import dns.reversename
import whois
import requests
import ssl
import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize rich console for colorized output
console = Console()

# Output directory
OUTPUT_DIR = "output"

# Helper to print section headings
def print_section(title):
    console.print(Panel(Text(title, style="bold cyan"), expand=False))

# WHOIS lookup
def whois_lookup(domain):
    print_section("WHOIS Lookup")
    result = {}
    try:
        w = whois.whois(domain)
        for key, value in w.items():
            console.print(f"[bold]{key}[/bold]: {value}")
            result[key] = value
    except Exception as e:
        console.print(f"[red]WHOIS lookup failed: {e}[/red]")
    return result

# DNS records
def dns_lookup(domain):
    print_section("DNS Records")
    record_types = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]
    results = {}
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype, raise_on_no_answer=False)
            records = [str(rdata) for rdata in answers]
            console.print(f"[bold]{rtype}[/bold]: {records}")
            results[rtype] = records
        except Exception as e:
            console.print(f"[yellow]{rtype} lookup failed: {e}[/yellow]")
            results[rtype] = None
    return results

# Reverse DNS lookup
def reverse_dns_lookup(domain):
    print_section("Reverse DNS Lookup")
    result = {}
    try:
        ip = socket.gethostbyname(domain)
        rev_name = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(rev_name, "PTR")
        ptrs = [str(rdata) for rdata in answers]
        console.print(f"[bold]PTR[/bold]: {ptrs}")
        result["PTR"] = ptrs
    except Exception as e:
        console.print(f"[red]Reverse DNS lookup failed: {e}[/red]")
        result["PTR"] = None
    return result

# SSL certificate details
def ssl_certificate_details(domain):
    print_section("SSL Certificate Details")
    result = {}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                console.print(cert)
                result = cert
    except Exception as e:
        console.print(f"[yellow]SSL certificate not available or error: {e}[/yellow]")
    return result

# Threat intelligence blacklist check (using AbuseIPDB public API as example)
def threat_intel_blacklist(domain):
    print_section("Threat Intelligence Blacklist Check")
    result = {}
    try:
        ip = socket.gethostbyname(domain)
        # AbuseIPDB public API (demo, limited)
        url = f"https://api.abuseipdb.com/api/v2/check"
        headers = {"Key": "demo"}  # Replace 'demo' with your API key for production
        params = {"ipAddress": ip, "maxAgeInDays": "90"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            console.print(data)
            result = data
        else:
            console.print(f"[yellow]AbuseIPDB API error: {response.status_code}[/yellow]")
    except Exception as e:
        console.print(f"[red]Threat intelligence check failed: {e}[/red]")
    return result

# Shodan query (optional, requires API key)
def shodan_query(domain, shodan_api_key=None):
    print_section("Shodan Query")
    result = {}
    if not shodan_api_key:
        console.print("[yellow]No Shodan API key provided. Skipping.[/yellow]")
        return result
    try:
        ip = socket.gethostbyname(domain)
        url = f"https://api.shodan.io/shodan/host/{ip}?key={shodan_api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            open_ports = data.get("ports", [])
            banners = [item.get("data", "") for item in data.get("data", [])]
            console.print(f"[bold]Open Ports:[/bold] {open_ports}")
            console.print(f"[bold]Banners:[/bold] {banners}")
            result = data
        else:
            console.print(f"[yellow]Shodan API error: {response.status_code}[/yellow]")
    except Exception as e:
        console.print(f"[red]Shodan query failed: {e}[/red]")
    return result

# Save results to timestamped JSON and text files
def save_results(domain, results):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, f"{domain}_{timestamp}.json")
    txt_path = os.path.join(OUTPUT_DIR, f"{domain}_{timestamp}.txt")
    # Save JSON
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    # Save text
    with open(txt_path, "w") as f:
        for section, data in results.items():
            f.write(f"==== {section} ====" + "\n")
            f.write(str(data) + "\n\n")
    console.print(f"[green]Results saved to {json_path} and {txt_path}[/green]")

# Main workflow
def main():
    parser = argparse.ArgumentParser(description="Advanced Python OSINT Tool Starter")
    parser.add_argument("domain", help="Domain name to query")
    parser.add_argument("--shodan", help="Shodan API key (optional)", default=None)
    args = parser.parse_args()

    domain = args.domain
    shodan_api_key = args.shodan

    results = {}
    results["WHOIS"] = whois_lookup(domain)
    results["DNS Records"] = dns_lookup(domain)
    results["Reverse DNS"] = reverse_dns_lookup(domain)
    results["SSL Certificate"] = ssl_certificate_details(domain)
    results["Threat Intelligence"] = threat_intel_blacklist(domain)
    results["Shodan"] = shodan_query(domain, shodan_api_key)

    save_results(domain, results)

# Entry point
if __name__ == "__main__":
    main()

# WHOIS lookup
def whois_lookup(domain):
    print_section("WHOIS Lookup")
    try:
        w = whois.whois(domain)
        for key, value in w.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"WHOIS lookup failed: {e}")

# DNS records
def dns_lookup(domain):
    print_section("DNS Records")
    record_types = ["A", "AAAA", "MX", "TXT", "NS", "CNAME"]
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype, raise_on_no_answer=False)
            print(f"{rtype}:")
            for rdata in answers:
                print(f"  {rdata}")
        except Exception as e:
            print(f"  {rtype} lookup failed: {e}")

# Reverse DNS lookup
def reverse_dns_lookup(domain):
    print_section("Reverse DNS Lookup")
    try:
        ip = socket.gethostbyname(domain)
        rev_name = dns.reversename.from_address(ip)
        answers = dns.resolver.resolve(rev_name, "PTR")
        for rdata in answers:
            print(f"PTR: {rdata}")
    except Exception as e:
        print(f"Reverse DNS lookup failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python OSINT Tool Starter")
    parser.add_argument("domain", help="Domain name to query")
    args = parser.parse_args()

    domain = args.domain
    whois_lookup(domain)
    dns_lookup(domain)
    reverse_dns_lookup(domain)
