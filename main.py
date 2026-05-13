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
    ctx.obj = AddonManager(config, registry, scanner)

@cli.command()
@click.argument('name')
@click.argument('url')
@click.pass_context
def install(ctx, name, url):
    """Install an addon from a URL."""
    ctx.obj.install_from_url(name, url)

@cli.command()
@click.pass_context
def update(ctx):
    """Update all managed addons."""
    ctx.obj.update_all()

@cli.command(name='list')
@click.pass_context
def list_addons(ctx):
    """List installed addons."""
    click.echo("Installed Addons:")
    addons = ctx.obj.registry.list_addons()
    if not addons:
        click.echo("  No addons installed via WAM.")
    for name, info in addons.items():
        click.echo(f"- {name} ({info['version']})")

@cli.command()
@click.argument('name')
@click.pass_context
def remove(ctx, name):
    """Remove an addon."""
    ctx.obj.remove_addon(name)

if __name__ == '__main__':
    cli()
