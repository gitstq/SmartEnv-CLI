"""SmartEnv-CLI command-line interface."""

import sys
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from smartenv.core import EnvFileManager, EnvSyncManager, EnvSecurityManager

console = Console()


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════╗
    ║   SmartEnv-CLI v1.0.0                     ║
    ║   Intelligent Environment Manager         ║
    ╚═══════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


@click.group()
@click.version_option(version="1.0.0", prog_name="smartenv")
@click.pass_context
def cli(ctx):
    """SmartEnv-CLI - Intelligent environment variable manager for developers."""
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        print_banner()
        console.print("\n[bold green]Run 'smartenv --help' for available commands.[/bold green]\n")


@cli.command()
@click.option("--path", "-p", default=".", help="Project path to analyze")
@click.option("--output", "-o", default=".env.example", help="Output file path")
def init(path: str, output: str):
    """Initialize .env.example by auto-detecting project type."""
    print_banner()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing project...", total=None)
        
        manager = EnvFileManager()
        profile = manager.detect_project_type(path)
        
        progress.update(task, description=f"Detected [bold]{profile.name}[/bold] project")
        
        example_vars = manager.generate_example(path)
        manager.write_env_file(example_vars, output)
        
        progress.update(task, description=f"Generated [bold green]{output}[/bold green]")
    
    # Display results
    table = Table(title=f"Detected Variables for {profile.name}")
    table.add_column("Variable", style="cyan", no_wrap=True)
    table.add_column("Default Value", style="green")
    table.add_column("Sensitive", style="red")
    table.add_column("Description", style="yellow")
    
    for key, var in example_vars.items():
        table.add_row(
            key,
            var.value[:50] + "..." if len(var.value) > 50 else var.value,
            "Yes" if var.is_sensitive else "No",
            var.comment or "-",
        )
    
    console.print(table)
    console.print(f"\n[bold green]Successfully created {output} with {len(example_vars)} variables![/bold green]")
    console.print("[dim]Tip: Fill in the values and rename to .env to get started.[/dim]\n")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
@click.option("--compare", "-c", required=True, help="Environment file to compare with")
def diff(env: str, compare: str):
    """Compare two .env files and show differences."""
    print_banner()
    
    if not Path(env).exists():
        console.print(f"[bold red]File not found: {env}[/bold red]")
        return
    
    if not Path(compare).exists():
        console.print(f"[bold red]File not found: {compare}[/bold red]")
        return
    
    manager = EnvFileManager(env)
    result = manager.compare_envs(compare)
    
    # Display missing in current
    if result["missing_in_current"]:
        console.print(Panel(
            "\n".join(f"  - [yellow]{key}[/yellow]" for key in result["missing_in_current"]),
            title=f"Missing in {env}",
            border_style="yellow",
        ))
    
    # Display missing in other
    if result["missing_in_other"]:
        console.print(Panel(
            "\n".join(f"  - [yellow]{key}[/yellow]" for key in result["missing_in_other"]),
            title=f"Missing in {compare}",
            border_style="yellow",
        ))
    
    # Display different values
    if result["different_values"]:
        table = Table(title="Different Values")
        table.add_column("Variable", style="cyan")
        table.add_column(f"Current ({env})", style="red")
        table.add_column(f"Other ({compare})", style="green")
        
        for item in result["different_values"]:
            table.add_row(
                item["key"],
                item["current"][:30] + "..." if len(item["current"]) > 30 else item["current"],
                item["other"][:30] + "..." if len(item["other"]) > 30 else item["other"],
            )
        
        console.print(table)
    
    # Display same values
    if result["same_values"]:
        console.print(Panel(
            "\n".join(f"  - [green]{key}[/green]" for key in result["same_values"]),
            title="Same Values",
            border_style="green",
        ))
    
    # Summary
    total_diffs = (
        len(result["missing_in_current"]) +
        len(result["missing_in_other"]) +
        len(result["different_values"])
    )
    
    if total_diffs == 0:
        console.print("\n[bold green]Perfect match! Both files are identical.[/bold green]\n")
    else:
        console.print(f"\n[bold yellow]Found {total_diffs} difference(s) between the files.[/bold yellow]\n")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
def validate(env: str):
    """Validate .env file for common issues and security risks."""
    print_banner()
    
    if not Path(env).exists():
        console.print(f"[bold red]File not found: {env}[/bold red]")
        return
    
    manager = EnvFileManager(env)
    issues = manager.validate()
    
    if not issues:
        console.print(Panel(
            "[bold green]No issues found! Your .env file looks great.[/bold green]",
            title="Validation Result",
            border_style="green",
        ))
        return
    
    # Categorize issues
    errors = [i for i in issues if i["type"] == "error"]
    warnings = [i for i in issues if i["type"] == "warning"]
    
    if errors:
        table = Table(title="Errors")
        table.add_column("Variable", style="cyan")
        table.add_column("Issue", style="red")
        
        for issue in errors:
            table.add_row(issue["key"], issue["message"])
        
        console.print(table)
    
    if warnings:
        table = Table(title="Warnings")
        table.add_column("Variable", style="cyan")
        table.add_column("Issue", style="yellow")
        
        for issue in warnings:
            table.add_row(issue["key"], issue["message"])
        
        console.print(table)
    
    console.print(f"\n[bold yellow]Found {len(errors)} error(s) and {len(warnings)} warning(s).[/bold yellow]\n")


@cli.command()
@click.option("--template", "-t", default=".env.example", help="Template file path")
@click.option("--path", "-p", default=".", help="Project base path")
def sync(template: str, path: str):
    """Sync all .env files from template."""
    print_banner()
    
    if not Path(template).exists():
        console.print(f"[bold red]Template file not found: {template}[/bold red]")
        console.print("[dim]Run 'smartenv init' first to generate a template.[/dim]")
        return
    
    sync_manager = EnvSyncManager(path)
    results = sync_manager.sync_from_template(template)
    
    if not results:
        console.print("[bold yellow]No .env files found to sync.[/bold yellow]")
        return
    
    table = Table(title="Sync Results")
    table.add_column("File", style="cyan")
    table.add_column("Added Variables", style="green")
    table.add_column("Total Variables", style="blue")
    
    for filename, result in results.items():
        table.add_row(
            filename,
            str(len(result["added"])),
            str(result["total_vars"]),
        )
    
    console.print(table)
    console.print("\n[bold green]Sync completed successfully![/bold green]\n")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
@click.option("--output", "-o", help="Output file path (default: overwrite input)")
def encrypt(env: str, output: Optional[str]):
    """Encrypt sensitive values in .env file."""
    print_banner()
    
    if not Path(env).exists():
        console.print(f"[bold red]File not found: {env}[/bold red]")
        return
    
    security = EnvSecurityManager()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Encrypting sensitive values...", total=None)
        encrypted_keys = security.encrypt_env_file(env, output)
        progress.update(task, description="Encryption complete")
    
    if encrypted_keys:
        console.print(Panel(
            "\n".join(f"  - [cyan]{key}[/cyan]" for key in encrypted_keys),
            title=f"Encrypted {len(encrypted_keys)} variable(s)",
            border_style="green",
        ))
        console.print("\n[bold green]Sensitive values encrypted successfully![/bold green]")
        console.print("[dim]Your encryption key is stored in .smartenv.key[/dim]\n")
    else:
        console.print("[bold yellow]No sensitive values found to encrypt.[/bold yellow]\n")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
@click.option("--output", "-o", help="Output file path (default: overwrite input)")
def decrypt(env: str, output: Optional[str]):
    """Decrypt values in .env file."""
    print_banner()
    
    if not Path(env).exists():
        console.print(f"[bold red]File not found: {env}[/bold red]")
        return
    
    security = EnvSecurityManager()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Decrypting values...", total=None)
        decrypted_keys = security.decrypt_env_file(env, output)
        progress.update(task, description="Decryption complete")
    
    if decrypted_keys:
        console.print(Panel(
            "\n".join(f"  - [cyan]{key}[/cyan]" for key in decrypted_keys),
            title=f"Decrypted {len(decrypted_keys)} variable(s)",
            border_style="green",
        ))
        console.print("\n[bold green]Values decrypted successfully![/bold green]\n")
    else:
        console.print("[bold yellow]No encrypted values found.[/bold yellow]\n")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
def show(env: str):
    """Display .env file contents with syntax highlighting."""
    print_banner()
    
    if not Path(env).exists():
        console.print(f"[bold red]File not found: {env}[/bold red]")
        return
    
    with open(env, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Mask sensitive values
    manager = EnvFileManager(env)
    variables = manager.parse_env_file()
    
    display_content = content
    for key, var in variables.items():
        if var.is_sensitive and var.value and not var.value.startswith("ENC("):
            display_content = display_content.replace(
                f'{key}="{var.value}"',
                f'{key}="***MASKED***"'
            )
    
    syntax = Syntax(display_content, "bash", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"{env}", border_style="blue"))
    
    # Summary
    sensitive_count = sum(1 for v in variables.values() if v.is_sensitive)
    console.print(f"\n[dim]Total: {len(variables)} variables | Sensitive: {sensitive_count}[/dim]\n")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
@click.argument("key")
@click.argument("value")
def setvar(env: str, key: str, value: str):
    """Set a specific environment variable."""
    manager = EnvFileManager(env)
    variables = manager.parse_env_file()
    
    is_sensitive = any(
        pattern.lower() in key.lower()
        for pattern in ["password", "secret", "token", "key", "private", "auth"]
    )
    
    variables[key] = type('EnvVariable', (), {
        'key': key,
        'value': value,
        'comment': '',
        'is_sensitive': is_sensitive,
        'source': env,
    })()
    
    manager.write_env_file(variables)
    
    console.print(f"[bold green]Set {key} in {env}[/bold green]")
    if is_sensitive:
        console.print("[dim]Detected as sensitive variable[/dim]")


@cli.command()
@click.option("--env", "-e", default=".env", help="Environment file path")
@click.argument("key")
def getvar(env: str, key: str):
    """Get the value of a specific environment variable."""
    manager = EnvFileManager(env)
    variables = manager.parse_env_file()
    
    if key not in variables:
        console.print(f"[bold red]Variable '{key}' not found in {env}[/bold red]")
        return
    
    var = variables[key]
    if var.is_sensitive:
        console.print(f"[cyan]{key}[/cyan]=[dim]***MASKED***[/dim]")
    else:
        console.print(f"[cyan]{key}[/cyan]=[green]{var.value}[/green]")


@cli.command()
def doctor():
    """Check SmartEnv-CLI installation and dependencies."""
    print_banner()
    
    table = Table(title="System Check")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Version", style="yellow")
    
    # Check Python
    import platform
    table.add_row("Python", "OK", platform.python_version())
    
    # Check dependencies
    deps = ["click", "rich", "cryptography", "yaml"]
    for dep in deps:
        try:
            if dep == "yaml":
                import yaml
                table.add_row("PyYAML", "OK", yaml.__version__)
            else:
                mod = __import__(dep)
                version = getattr(mod, "__version__", "unknown")
                table.add_row(dep.capitalize(), "OK", version)
        except ImportError:
            table.add_row(dep.capitalize(), "Missing", "-")
    
    console.print(table)
    console.print("\n")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
