import click
import os
import logging
from pathlib import Path
from config import ConfigManager
from registry import RegistryManager
from scanner import AddonScanner
from manager import AddonManager

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@click.group()
@click.pass_context
def cli(ctx):
    """WAM: World of Warcraft Addon Manager."""
    config = ConfigManager()
    # Registry path is relative to the script location for now
    reg_path = Path(__file__).parent / ".wam_registry.json"
    registry = RegistryManager(reg_path)
    scanner = AddonScanner(config.get_wow_path())
    ctx.obj = {
        'manager': AddonManager(config, registry, scanner),
        'config': config
    }

@cli.command()
@click.option('--path', help='Set the absolute path to your WoW AddOns directory.')
@click.option('--api-key', help='Set your CurseForge API key.')
@click.pass_context
def config(ctx, path, api_key):
    """View or update configuration."""
    config_mgr = ctx.obj['config']
    if path or api_key:
        config_mgr.save_config(wow_path=path, api_key=api_key)
        if path:
            click.echo(f"Success: WoW path set to {path}")
            if not config_mgr.is_path_valid():
                click.echo("Warning: The provided path does not exist or is not a directory.")
        if api_key:
            click.echo("Success: CurseForge API key updated.")
    else:
        click.echo(f"Current WoW Path: {config_mgr.get_wow_path()}")
        if config_mgr.is_path_valid():
            click.echo("Status: Path is valid.")
        else:
            click.echo("Status: Path is INVALID. Use 'python main.py config --path <path>' to fix it.")
        
        has_key = "Yes" if config_mgr.config.get("api_key") else "No"
        click.echo(f"CurseForge API Key set: {has_key}")

def validate_path(ctx):
    config_mgr = ctx.obj['config']
    if not config_mgr.is_path_valid():
        click.echo(f"Error: Invalid WoW path configured: {config_mgr.get_wow_path()}")
        click.echo("Please set a valid path using: python main.py config --path <path>")
        ctx.exit(1)

@cli.command()
@click.argument('name')
@click.argument('url')
@click.pass_context
def install(ctx, name, url):
    """Install an addon from a URL."""
    validate_path(ctx)
    ctx.obj['manager'].install_from_url(name, url)

@cli.command()
@click.pass_context
def update(ctx):
    """Update all managed addons."""
    validate_path(ctx)
    ctx.obj['manager'].update_all()

@cli.command()
@click.pass_context
def sync(ctx):
    """Sync existing addons from the WoW folder."""
    validate_path(ctx)
    ctx.obj['manager'].sync_with_folder()

@cli.command(name='list')
@click.pass_context
def list_addons(ctx):
    """List installed addons."""
    # List doesn't strictly need a valid WoW path to show what's in the registry
    click.echo("Installed Addons:")
    addons = ctx.obj['manager'].registry.list_addons()
    if not addons:
        click.echo("  No addons installed via WAM.")
    for name, info in addons.items():
        click.echo(f"- {name} ({info['version']})")

@cli.command()
@click.argument('name')
@click.pass_context
def remove(ctx, name):
    """Remove an addon."""
    validate_path(ctx)
    ctx.obj['manager'].remove_addon(name)

if __name__ == '__main__':
    cli()
