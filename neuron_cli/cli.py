#!/usr/bin/env python3
"""
Neuron CLI - AI-powered full-stack code generation
"""

import os
import sys
import json
import click
import requests
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

# Load environment variables
load_dotenv()

console = Console()

# Configuration
NEURON_API_URL = os.getenv("NEURON_API_URL", "http://localhost:8000")
CONFIG_FILE = Path.home() / ".neuron" / "config.json"


class NeuronConfig:
    """Manage Neuron CLI configuration"""
    
    @staticmethod
    def ensure_config_dir():
        """Ensure config directory exists"""
        config_dir = Path.home() / ".neuron"
        config_dir.mkdir(exist_ok=True)
        return config_dir
    
    @staticmethod
    def load_config():
        """Load configuration from file"""
        NeuronConfig.ensure_config_dir()
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_config(config):
        """Save configuration to file"""
        NeuronConfig.ensure_config_dir()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def get_current_project():
        """Get current project from config"""
        config = NeuronConfig.load_config()
        return config.get("current_project")
    
    @staticmethod
    def set_current_project(project_path):
        """Set current project in config"""
        config = NeuronConfig.load_config()
        config["current_project"] = str(project_path)
        NeuronConfig.save_config(config)


def make_api_request(endpoint, method="GET", data=None):
    """Make API request to Neuron backend"""
    url = f"{NEURON_API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        console.print("[red]❌ Error: Cannot connect to Neuron backend[/red]")
        console.print(f"[yellow]Make sure the backend is running at {NEURON_API_URL}[/yellow]")
        sys.exit(1)
    
    except requests.exceptions.HTTPError as e:
        console.print(f"[red]❌ API Error: {e}[/red]")
        if hasattr(e.response, 'json'):
            try:
                error_data = e.response.json()
                console.print(f"[red]{error_data.get('message', 'Unknown error')}[/red]")
            except:
                pass
        sys.exit(1)
    
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    🧠 Neuron - AI-powered full-stack code generation
    
    Build features with AI assistance for your React + Express projects.
    """
    pass


@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def init(project_path):
    """
    Initialize a project with Neuron
    
    Example: neuron init /path/to/project
    """
    project_path = Path(project_path).resolve()
    
    console.print(Panel.fit(
        f"[cyan]Initializing Neuron for project:[/cyan]\n[white]{project_path}[/white]",
        title="🧠 Neuron Init"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Setting up project...", total=None)
        
        # Set project in backend
        response = make_api_request(
            "/set-project",
            method="POST",
            data={"project_path": str(project_path)}
        )
        
        # Save to local config
        NeuronConfig.set_current_project(project_path)
        
        progress.update(task, completed=True)
    
    console.print(f"\n[green]✓ Project initialized successfully![/green]")
    console.print(f"[dim]Project: {response['project_name']}[/dim]")
    console.print(f"[dim]Path: {response['project_path']}[/dim]")
    
    # Show analysis summary
    analysis = response.get('analysis', {})
    console.print(f"\n[cyan]Project Summary:[/cyan]")
    console.print(f"  • Backend files: {analysis.get('backend_files', 0)}")
    console.print(f"  • Frontend files: {analysis.get('frontend_files', 0)}")
    console.print(f"  • Has package.json: {'✓' if analysis.get('has_package_json') else '✗'}")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True), required=False)
def analyze(project_path):
    """
    Analyze project structure and provide a detailed report
    
    Examples:
        neuron analyze /path/to/project
        neuron analyze  (uses current project)
    """
    if not project_path:
        project_path = NeuronConfig.get_current_project()
        if not project_path:
            console.print("[red]❌ No project specified and no current project set[/red]")
            console.print("[yellow]Use 'neuron init <path>' first or specify a project path[/yellow]")
            sys.exit(1)
    else:
        project_path = Path(project_path).resolve()
        # Set as current project
        response = make_api_request(
            "/set-project",
            method="POST",
            data={"project_path": str(project_path)}
        )
    
    console.print(Panel.fit(
        f"[cyan]Analyzing project:[/cyan]\n[white]{project_path}[/white]",
        title="🔍 Project Analysis"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Scanning project files...", total=None)
        
        response = make_api_request("/analyze")
        
        progress.update(task, completed=True)
    
    if response['status'] != 'success':
        console.print(f"[red]❌ Analysis failed: {response.get('message', 'Unknown error')}[/red]")
        sys.exit(1)
    
    analysis = response['analysis']
    
    # Display summary
    console.print("\n[bold cyan]📊 Project Summary[/bold cyan]")
    console.print("─" * 50)
    
    # Tech Stack
    console.print("\n[bold yellow]🚀 Tech Stack Detected[/bold yellow]")
    tech_stack = analysis.get('tech_stack', {})
    
    # Frontend tech
    if tech_stack.get('frontend'):
        console.print("\n[cyan]Frontend:[/cyan]")
        for tech, confidence in tech_stack['frontend'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {tech.capitalize()} ({confidence} confidence)")
    
    # Backend tech
    if tech_stack.get('backend'):
        console.print("\n[cyan]Backend:[/cyan]")
        for tech, confidence in tech_stack['backend'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {tech.capitalize()} ({confidence} confidence)")
    
    # Language
    if tech_stack.get('language'):
        console.print("\n[cyan]Languages:[/cyan]")
        for lang, confidence in tech_stack['language'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {lang.capitalize()} ({confidence} confidence)")
    
    # Database
    if tech_stack.get('database'):
        console.print("\n[cyan]Database:[/cyan]")
        for db, confidence in tech_stack['database'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {db.capitalize()} ({confidence} confidence)")
    
    # ORM
    if tech_stack.get('orm'):
        console.print("\n[cyan]ORM/ODM:[/cyan]")
        for orm, confidence in tech_stack['orm'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {orm.capitalize()} ({confidence} confidence)")
    
    # State Management
    if tech_stack.get('state_management'):
        console.print("\n[cyan]State Management:[/cyan]")
        for state, confidence in tech_stack['state_management'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {state.capitalize()} ({confidence} confidence)")
    
    # Styling
    if tech_stack.get('styling'):
        console.print("\n[cyan]Styling:[/cyan]")
        for style, confidence in tech_stack['styling'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {style.capitalize()} ({confidence} confidence)")
    
    # Testing
    if tech_stack.get('testing'):
        console.print("\n[cyan]Testing:[/cyan]")
        for test, confidence in tech_stack['testing'].items():
            icon = "🟢" if confidence == "high" else "🟡"
            console.print(f"  {icon} {test.capitalize()} ({confidence} confidence)")
    
    # Backend summary
    backend = analysis.get('backend', {})
    if backend.get('exists'):
        console.print("\n[bold yellow]📦 Backend Structure[/bold yellow]")
        framework = backend.get('detected_framework', 'Unknown')
        console.print(f"  Framework: [white]{framework.capitalize()}[/white]")
        console.print(f"  Total files: [white]{backend.get('file_count', 0)}[/white]")
        
        structure = backend.get('structure', {})
        if structure:
            console.print("\n  [dim]File Organization:[/dim]")
            for category, info in structure.items():
                count = info.get('count', 0) if isinstance(info, dict) else len(info)
                if count > 0:
                    console.print(f"    • {category.capitalize()}: {count} files")
                    
                    # Show sample files
                    files = info.get('files', []) if isinstance(info, dict) else info
                    if files and len(files) <= 3:
                        for f in files:
                            console.print(f"      - {f}")
                    elif files and len(files) > 3:
                        for f in files[:2]:
                            console.print(f"      - {f}")
                        console.print(f"      ... and {len(files) - 2} more")
    else:
        console.print("\n[yellow]Backend: ✗ Not detected[/yellow]")
    
    # Frontend summary
    frontend = analysis.get('frontend', {})
    if frontend.get('exists'):
        console.print("\n[bold yellow]🎨 Frontend Structure[/bold yellow]")
        framework = frontend.get('detected_framework', 'Unknown')
        console.print(f"  Framework: [white]{framework.capitalize()}[/white]")
        console.print(f"  Total files: [white]{frontend.get('file_count', 0)}[/white]")
        
        structure = frontend.get('structure', {})
        if structure:
            console.print("\n  [dim]File Organization:[/dim]")
            for category, info in structure.items():
                count = info.get('count', 0) if isinstance(info, dict) else len(info)
                if count > 0:
                    console.print(f"    • {category.capitalize()}: {count} files")
                    
                    # Show sample files
                    files = info.get('files', []) if isinstance(info, dict) else info
                    if files and len(files) <= 3:
                        for f in files:
                            console.print(f"      - {f}")
                    elif files and len(files) > 3:
                        for f in files[:2]:
                            console.print(f"      - {f}")
                        console.print(f"      ... and {len(files) - 2} more")
    else:
        console.print("\n[yellow]Frontend: ✗ Not detected[/yellow]")
    
    # Insights
    insights = analysis.get('insights', [])
    if insights:
        console.print("\n[bold yellow]💡 Insights & Recommendations[/bold yellow]")
        
        # Group by level
        success_insights = [i for i in insights if i.get('level') == 'success']
        info_insights = [i for i in insights if i.get('level') == 'info']
        warning_insights = [i for i in insights if i.get('level') == 'warning']
        
        if success_insights:
            console.print("\n[green]✓ Good Practices:[/green]")
            for insight in success_insights:
                console.print(f"  • {insight['message']}")
        
        if info_insights:
            console.print("\n[cyan]ℹ Information:[/cyan]")
            for insight in info_insights:
                console.print(f"  • {insight['message']}")
        
        if warning_insights:
            console.print("\n[yellow]⚠ Recommendations:[/yellow]")
            for insight in warning_insights:
                console.print(f"  • {insight['message']}")
    
    # Environment files
    env_files = analysis.get('env_files', [])
    if env_files:
        console.print("\n[yellow]Configuration Files:[/yellow]")
        for env_file in env_files:
            console.print(f"  ✓ {env_file}")
    
    # Package.json status
    console.print("\n[yellow]Package Management:[/yellow]")
    has_package = analysis.get('has_package_json', False)
    has_requirements = analysis.get('has_requirements_txt', False)
    
    if has_package:
        console.print(f"  ✓ package.json found")
    if has_requirements:
        console.print(f"  ✓ requirements.txt found")
    if not has_package and not has_requirements:
        console.print(f"  ✗ No package management files found")
    
    console.print("\n[green]✓ Analysis complete![/green]")

    
@cli.command()
@click.argument('feature', required=True)
@click.option('--project', '-p', type=click.Path(exists=True), help='Project path (optional if initialized)')
def build(feature, project):
    """
    Build a new feature with AI assistance
    
    Examples:
        neuron build "Add user login with email and password"
        neuron build "Create shopping cart functionality" -p /path/to/project
    """
    if project:
        project_path = Path(project).resolve()
        # Set as current project
        response = make_api_request(
            "/set-project",
            method="POST",
            data={"project_path": str(project_path)}
        )
    else:
        project_path = NeuronConfig.get_current_project()
        if not project_path:
            console.print("[red]❌ No project specified and no current project set[/red]")
            console.print("[yellow]Use 'neuron init <path>' first or use --project flag[/yellow]")
            sys.exit(1)
    
    console.print(Panel.fit(
        f"[cyan]Building feature:[/cyan]\n[white]{feature}[/white]\n\n[dim]Project: {project_path}[/dim]",
        title="🚀 Feature Builder"
    ))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task1 = progress.add_task("[cyan]Creating architecture plan...", total=None)
        
        # Build feature
        response = make_api_request(
            "/build-and-save",
            method="POST",
            data={"feature": feature}
        )
        
        progress.update(task1, completed=True)
        
        if response['status'] != 'success':
            console.print(f"[red]❌ Build failed: {response.get('message', 'Unknown error')}[/red]")
            sys.exit(1)
        
        task2 = progress.add_task("[cyan]Generating code...", total=None)
        progress.update(task2, completed=True)
        
        task3 = progress.add_task("[cyan]Saving files...", total=None)
        progress.update(task3, completed=True)
    
    # Show results
    console.print("\n[bold green]✓ Feature built successfully![/bold green]")
    
    if response['request_type'] == 'FEATURE':
        saved_files = response.get('saved_files', [])
        
        console.print(f"\n[cyan]Files created/modified:[/cyan]")
        
        # Group by type
        backend_files = [f for f in saved_files if f['type'] == 'backend']
        frontend_files = [f for f in saved_files if f['type'] == 'frontend']
        
        if backend_files:
            console.print("\n[yellow]Backend:[/yellow]")
            for file_info in backend_files:
                action_icon = "✨" if file_info['action'] == 'create' else "🔄"
                console.print(f"  {action_icon} {file_info['path']}")
        
        if frontend_files:
            console.print("\n[yellow]Frontend:[/yellow]")
            for file_info in frontend_files:
                action_icon = "✨" if file_info['action'] == 'create' else "🔄"
                console.print(f"  {action_icon} {file_info['path']}")
        
        console.print(f"\n[dim]Total: {len(saved_files)} files[/dim]")
    
    console.print("\n[green]Next steps:[/green]")
    console.print("  1. Review the generated code")
    console.print("  2. Install any new dependencies: npm install")
    console.print("  3. Test the new feature")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True), required=False)
def verify(project_path):
    """
    Verify project for issues and provide recommendations

    Examples:
        neuron verify
        neuron verify /path/to/project
    """
    if not project_path:
        project_path = NeuronConfig.get_current_project()
        if not project_path:
            console.print("[red]❌ No project specified and no current project set[/red]")
            console.print("[yellow]Use 'neuron init <path>' first[/yellow]")
            sys.exit(1)
    else:
        project_path = Path(project_path).resolve()
        make_api_request(
            "/set-project",
            method="POST",
            data={"project_path": str(project_path)}
        )

    console.print(Panel.fit(
        f"[cyan]Verifying project:[/cyan]\n[white]{project_path}[/white]",
        title="🔍 Project Verification"
    ))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Checking for issues...", total=None)

        response = make_api_request(
            "/build-and-save",
            method="POST",
            data={"feature": "verify project"}
        )

        progress.update(task, completed=True)

    if response['status'] != 'success':
        console.print(f"[red]❌ Verification failed: {response.get('message', 'Unknown error')}[/red]")
        sys.exit(1)

    analysis = response['analysis']
    summary = analysis['summary']

    console.print(f"\n[bold cyan]Verification Results[/bold cyan]")
    console.print("─" * 50)

    severity_colors = {
        'healthy': 'green',
        'info': 'blue',
        'warning': 'yellow',
        'critical': 'red'
    }

    severity = summary['severity']
    color = severity_colors.get(severity, 'white')

    console.print(f"\n[{color}]Status: {severity.upper()}[/{color}]")
    console.print(f"Issues found: {summary['issues_found']}")

    if analysis['issues']:
        console.print("\n[yellow]Issues:[/yellow]")
        for issue in analysis['issues']:
            icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(issue['severity'], '⚪')
            console.print(f"\n  {icon} [{issue['severity'].upper()}] {issue['type']}")
            console.print(f"     File: {issue['file']}")
            console.print(f"     {issue['description']}")

    if analysis['recommendations']:
        console.print("\n[green]Recommendations:[/green]")
        for i, rec in enumerate(analysis['recommendations'], 1):
            console.print(f"  {i}. {rec}")


@cli.command()
def status():
    """Show current project status and configuration"""
    current_project = NeuronConfig.get_current_project()
    
    console.print("\n[bold cyan]Neuron Status[/bold cyan]")
    console.print("─" * 50)
    
    if current_project:
        console.print(f"\n[green]✓ Current Project:[/green]")
        console.print(f"  {current_project}")
        
        # Get features
        try:
            response = make_api_request("/project-features")
            features = response.get('features', [])
            
            if features:
                console.print(f"\n[cyan]Features Added ({len(features)}):[/cyan]")
                for feature in features[-5:]:
                    console.print(f"  • {feature['name']}")
                    console.print(f"    [dim]{feature['added_at']}[/dim]")
                
                if len(features) > 5:
                    console.print(f"  [dim]... and {len(features) - 5} more[/dim]")
        except:
            pass
    else:
        console.print("\n[yellow]No project initialized[/yellow]")
        console.print("Use 'neuron init <path>' to get started")
    
    # Show API connection
    console.print(f"\n[cyan]Backend:[/cyan]")
    try:
        health = make_api_request("/health")
        console.print(f"  [green]✓ Connected to {NEURON_API_URL}[/green]")
    except:
        console.print(f"  [red]✗ Cannot connect to {NEURON_API_URL}[/red]")


@cli.command()
def projects():
    """List all projects"""
    console.print("\n[bold cyan]Neuron Projects[/bold cyan]")
    console.print("─" * 50)
    
    try:
        response = make_api_request("/list-projects")
        all_projects = response['data']['projects']
        current = response['data']['current']
        
        if not all_projects:
            console.print("\n[yellow]No projects found[/yellow]")
            console.print("Use 'neuron init <path>' to add a project")
            return
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Path", style="white")
        table.add_column("Features", justify="right")
        table.add_column("Last Accessed", style="dim")
        
        for name, data in all_projects.items():
            is_current = "→ " if name == current else "  "
            features_count = len(data.get('features_added', []))
            table.add_row(
                f"{is_current}{name}",
                data['path'],
                str(features_count),
                data.get('last_accessed', 'Unknown')[:10]
            )
        
        console.print("\n")
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error loading projects: {e}[/red]")


if __name__ == "__main__":
    cli()