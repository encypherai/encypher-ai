#!/usr/bin/env python3
"""
Docker Image Security Scanner for Encypher Commercial

Uses Trivy (via Docker) to scan all service images for vulnerabilities.

Usage:
    python scripts/scan_docker_images.py
"""
import json
import subprocess
import sys
from typing import Any, Dict

# Images to scan (built from docker-compose.microservices.yml)
IMAGES = [
    "encypherai-commercial-auth-service",
    "encypherai-commercial-key-service",
    "encypherai-commercial-billing-service",
    "encypherai-commercial-analytics-service",
    "encypherai-commercial-user-service",
    "encypherai-commercial-notification-service",
    "encypherai-commercial-encoding-service",
    "encypherai-commercial-verification-service",
    "encypherai-commercial-coalition-service",
    "encypherai-commercial-enterprise-api",
]

def run_trivy_scan(image: str) -> Dict[str, Any]:
    """Run Trivy scan on a Docker image using Docker."""
    try:
        # Run trivy via Docker
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", "/var/run/docker.sock:/var/run/docker.sock",
                "-v", "trivy-cache:/root/.cache/",
                "aquasec/trivy:latest",
                "image",
                "--format", "json",
                "--severity", "HIGH,CRITICAL",
                "--quiet",
                image
            ],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr or "Scan failed"}
    except subprocess.TimeoutExpired:
        return {"error": "Scan timed out"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}
    except Exception as e:
        return {"error": str(e)}

def run_simple_scan(image: str) -> Dict[str, Any]:
    """Run a simple Trivy scan with text output."""
    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", "/var/run/docker.sock:/var/run/docker.sock",
                "aquasec/trivy:latest",
                "image",
                "--severity", "HIGH,CRITICAL",
                "--no-progress",
                image
            ],
            capture_output=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )
        return {
            "output": result.stdout or "",
            "error": result.stderr if result.returncode != 0 else None,
            "returncode": result.returncode
        }
    except Exception as e:
        return {"error": str(e), "output": ""}

def check_image_exists(image: str) -> bool:
    """Check if a Docker image exists locally."""
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True
    )
    return result.returncode == 0

def main():
    print("=" * 60)
    print("Docker Image Security Scanner (Trivy)")
    print("=" * 60)
    
    # Check which images exist
    existing_images = []
    for image in IMAGES:
        if check_image_exists(image):
            existing_images.append(image)
            print(f"  [OK] {image}")
        else:
            print(f"  [--] {image} (not built)")
    
    if not existing_images:
        print("\nNo images to scan. Build images first:")
        print("  docker-compose -f docker-compose.microservices.yml build")
        return 1
    
    print(f"\nScanning {len(existing_images)} images for HIGH/CRITICAL vulnerabilities...")
    print("(This may take a few minutes on first run)\n")
    
    total_vulns = {"CRITICAL": 0, "HIGH": 0}
    results = {}
    
    for image in existing_images:
        print(f"\n{'='*40}")
        print(f"Scanning: {image}")
        print(f"{'='*40}")
        
        scan_result = run_simple_scan(image)
        
        if scan_result.get("error"):
            print(f"  Error: {scan_result['error']}")
            continue
        
        output = scan_result.get("output", "")
        
        # Count vulnerabilities from output
        critical_count = output.count("CRITICAL:")
        high_count = output.count("HIGH:")
        
        total_vulns["CRITICAL"] += critical_count
        total_vulns["HIGH"] += high_count
        
        if critical_count > 0 or high_count > 0:
            print(f"  CRITICAL: {critical_count}")
            print(f"  HIGH: {high_count}")
            # Show first few CVEs
            lines = output.split('\n')
            vuln_lines = [l for l in lines if 'CVE-' in l][:5]
            for line in vuln_lines:
                # Clean line for Windows console
                clean_line = line.strip()[:80].encode('ascii', 'replace').decode('ascii')
                print(f"    {clean_line}")
            if len(vuln_lines) < critical_count + high_count:
                print("    ... and more")
        else:
            print("  No HIGH/CRITICAL vulnerabilities found!")
        
        results[image] = {
            "critical": critical_count,
            "high": high_count
        }
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Images scanned: {len(existing_images)}")
    print(f"Total CRITICAL: {total_vulns['CRITICAL']}")
    print(f"Total HIGH: {total_vulns['HIGH']}")
    
    if total_vulns["CRITICAL"] > 0:
        print("\n[!] CRITICAL vulnerabilities found! Review and update base images.")
        return 1
    elif total_vulns["HIGH"] > 0:
        print("\n[!] HIGH vulnerabilities found. Consider updating packages.")
        return 1
    else:
        print("\n[OK] No HIGH/CRITICAL vulnerabilities found!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
