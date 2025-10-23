#!/usr/bin/env python
"""
Helper script to generate Ed25519 key pair for EncypherAI.

Generates a private and public key pair in PEM format and a suggested key_id.
Provides instructions for storing the private key securely (e.g., in a .env file)
and using the public key and key_id in your application.
"""

import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def generate_and_print_keys():
    """Generates and prints Ed25519 keys and instructions."""

    console.print(Panel("[bold cyan]EncypherAI Key Pair Generator[/bold cyan]", expand=False))

    # Generate private key
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Serialize private key to PEM format (PKCS8, unencrypted)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Serialize public key to PEM format (SubjectPublicKeyInfo)
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Generate a suggested key_id (timestamp-based)
    suggested_key_id = f"key_{int(time.time())}"

    # --- Output ---

    console.print("\n[bold green]Successfully generated a new Ed25519 key pair![/bold green]")

    console.print("\n[bold]1. Private Key (PEM Format):[/bold]")
    console.print("   [yellow]Store this key securely and NEVER commit it to version control.[/yellow]")
    console.print(Syntax(private_pem.decode("utf-8"), "pem", theme="default", line_numbers=False))

    console.print("\n[bold]2. Public Key (PEM Format):[/bold]")
    console.print("   Share this key with systems that need to verify your signed data.")
    console.print(Syntax(public_pem.decode("utf-8"), "pem", theme="default", line_numbers=False))

    console.print(f"\n[bold]3. Suggested Key ID:[/bold] [magenta]{suggested_key_id}[/magenta]")
    console.print("   Use this ID when embedding metadata (in the 'key_id' field)")
    console.print("   and configure your verifier's public_key_resolver to return the")
    console.print("   corresponding public key when given this ID.")

    console.print("\n[bold cyan]--- Usage Instructions ---[/bold cyan]")
    console.print("1. [bold]Save the Private Key:[/bold]")
    console.print("   - Add the entire Private Key PEM block (including -----BEGIN/END----- lines)")
    console.print("     to your environment variables or a secure secret store.")
    console.print("   - [bold]Example for .env file:[/bold]")
    # Prepare the PEM string for embedding in the example .env line
    private_pem_str_env = private_pem.decode("utf-8").strip().replace("\n", "\\n")
    console.print(f'     [cyan]ENCYPHER_PRIVATE_KEY="""{private_pem_str_env}"""[/cyan]')
    console.print("     (Ensure your .env loading mechanism handles multiline variables correctly, or store without newlines)")
    console.print("2. [bold]Load the Private Key in your app:[/bold]")
    console.print("   - Use `os.getenv('ENCYPHER_PRIVATE_KEY')` and `serialization.load_pem_private_key`.")
    console.print("     (See comments in example FastAPI app for loading code)")
    console.print("3. [bold]Use the Public Key & Key ID:[/bold]")
    # Construct the example dictionary string safely
    example_dict_str = f'{{ "key_id": "{suggested_key_id}" }}'
    console.print(f"   - When embedding metadata, ensure your metadata dictionary includes `{example_dict_str}`.")
    console.print("   - Configure your `public_key_resolver` function to return the Public Key PEM")
    console.print(f"     when it receives the key ID '{suggested_key_id}'.")


if __name__ == "__main__":
    generate_and_print_keys()
