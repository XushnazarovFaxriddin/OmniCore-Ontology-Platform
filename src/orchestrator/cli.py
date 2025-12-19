"""
OmniCore Platform v10 - Command Line Interface
Entry point for running the platform
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path

from .runner import OmniCoreOrchestrator, DeploymentMode, ServiceManager


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="omnicore",
        description="OmniCore Ontology Platform v10 - AI-Orchestrated Ontological Computing System"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start the platform")
    start_parser.add_argument(
        "--mode", "-m",
        choices=["venv", "docker", "podman"],
        default="venv",
        help="Deployment mode (default: venv)"
    )
    start_parser.add_argument(
        "--service", "-s",
        help="Start specific service only"
    )
    start_parser.add_argument(
        "--foreground", "-f",
        action="store_true",
        help="Run in foreground"
    )

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the platform")
    stop_parser.add_argument(
        "--mode", "-m",
        choices=["venv", "docker", "podman"],
        default="venv",
        help="Deployment mode"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show platform status")
    status_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )

    # Health command
    health_parser = subparsers.add_parser("health", help="Check service health")
    health_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )

    # Services command
    services_parser = subparsers.add_parser("services", help="List available services")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import an ontology")
    import_parser.add_argument("source", help="Ontology URL or file path")
    import_parser.add_argument(
        "--format", "-f",
        choices=["xml", "turtle", "n3", "nt", "json-ld"],
        default="turtle",
        help="Ontology format"
    )
    import_parser.add_argument(
        "--use-slm",
        action="store_true",
        help="Enable SLM enhancement"
    )

    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to previous MO version")
    rollback_parser.add_argument("version", help="Target version (e.g., mo:v1.2.0)")
    rollback_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without applying"
    )

    # SLM commands
    slm_parser = subparsers.add_parser("slm", help="SLM operations")
    slm_subparsers = slm_parser.add_subparsers(dest="slm_command")

    slm_status = slm_subparsers.add_parser("status", help="Check SLM status")
    slm_models = slm_subparsers.add_parser("models", help="List available models")
    slm_pull = slm_subparsers.add_parser("pull", help="Pull a model")
    slm_pull.add_argument("model", help="Model name (e.g., llama3.2:1b)")

    # Strategic command
    strategic_parser = subparsers.add_parser("strategic", help="Strategic AI operations")
    strategic_subparsers = strategic_parser.add_subparsers(dest="strategic_command")

    strategic_review = strategic_subparsers.add_parser("review", help="Run strategic review")
    strategic_status = strategic_subparsers.add_parser("status", help="Get oversight status")

    return parser


async def cmd_start(args):
    """Handle start command"""
    mode = DeploymentMode(args.mode)
    orchestrator = OmniCoreOrchestrator(mode=mode)

    if args.service:
        # Start specific service
        manager = ServiceManager()
        success = await manager.start_service(args.service)
        sys.exit(0 if success else 1)

    if args.foreground:
        # Run in foreground
        await orchestrator.run_forever()
    else:
        # Start and return
        success = await orchestrator.start()
        if success:
            print("OmniCore v10 started successfully!")
            print(f"API Gateway: http://localhost:18000")
            print(f"Dashboard: http://localhost:3000")
            print("\nServices started:")
            for name, info in orchestrator.get_status()["services"].items():
                print(f"  - {name}: {info['status']} (port {info['port']})")
        else:
            print("Failed to start OmniCore v10")
            sys.exit(1)


async def cmd_stop(args):
    """Handle stop command"""
    mode = DeploymentMode(args.mode)
    orchestrator = OmniCoreOrchestrator(mode=mode)
    await orchestrator.stop()
    print("OmniCore v10 stopped")


async def cmd_status(args):
    """Handle status command"""
    orchestrator = OmniCoreOrchestrator()
    status = orchestrator.get_status()

    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print("OmniCore Platform v10 Status")
        print("=" * 40)
        print(f"Mode: {status['mode']}")
        print(f"Running: {status['running']}")
        print(f"\nSettings:")
        for k, v in status['settings'].items():
            print(f"  {k}: {v}")
        print(f"\nServices:")
        for name, info in status['services'].items():
            status_str = info['status']
            gpu = " (GPU)" if info['gpu_required'] else ""
            print(f"  {name}: {status_str} - port {info['port']}{gpu}")


async def cmd_health(args):
    """Handle health command"""
    orchestrator = OmniCoreOrchestrator()
    health = await orchestrator.health_check()

    if args.json:
        print(json.dumps(health, indent=2))
    else:
        print("Service Health Check")
        print("=" * 40)
        all_healthy = True
        for name, healthy in health.items():
            status = "✓ healthy" if healthy else "✗ unhealthy"
            print(f"  {name}: {status}")
            if not healthy:
                all_healthy = False

        print()
        if all_healthy:
            print("All services healthy!")
        else:
            print("Some services are unhealthy!")
            sys.exit(1)


def cmd_services(args):
    """Handle services command"""
    print("Available Services")
    print("=" * 40)
    for name, config in ServiceManager.SERVICES.items():
        deps = ", ".join(config.depends_on) if config.depends_on else "none"
        gpu = " (GPU required)" if config.gpu_required else ""
        print(f"\n{name}:")
        print(f"  Name: {config.name}")
        print(f"  Port: {config.port}")
        print(f"  Dependencies: {deps}")
        print(f"  Module: {config.module}{gpu}")


async def cmd_import(args):
    """Handle import command"""
    from rdf.parser import OntologyImporter
    from common.models import OntologyImportRequest

    print(f"Importing ontology from: {args.source}")

    importer = OntologyImporter()

    # Check if file or URL
    source_path = Path(args.source)
    if source_path.exists():
        with open(source_path) as f:
            content = f.read()
        request = OntologyImportRequest(
            content=content,
            format=args.format,
            use_slm=args.use_slm,
            conflict_resolution="auto"
        )
    else:
        request = OntologyImportRequest(
            source_url=args.source,
            format=args.format,
            use_slm=args.use_slm,
            conflict_resolution="auto"
        )

    result = await importer.import_ontology(request)

    print("\nImport Result:")
    print("=" * 40)
    print(f"Success: {result.success}")
    print(f"Version: {result.version}")
    print(f"Triples imported: {result.triples_imported}")
    print(f"Entities created: {result.entities_created}")
    print(f"Causality links: {result.causality_links_created}")
    print(f"Epistemic annotations: {result.epistemic_annotations_created}")
    print(f"Conflicts detected: {result.conflicts_detected}")
    print(f"Conflicts resolved: {result.conflicts_resolved}")
    print(f"SLM enhancements: {result.slm_enhancements}")
    print(f"Processing time: {result.processing_time_ms:.2f}ms")

    if result.errors:
        print(f"\nErrors:")
        for err in result.errors:
            print(f"  - {err}")

    if result.warnings:
        print(f"\nWarnings:")
        for warn in result.warnings:
            print(f"  - {warn}")


async def cmd_slm(args):
    """Handle SLM commands"""
    from ai.slm.client import get_slm_client

    client = get_slm_client()

    if args.slm_command == "status":
        health = await client.health_check()
        print("SLM Provider Status")
        print("=" * 40)
        for provider, healthy in health.items():
            status = "✓ available" if healthy else "✗ unavailable"
            print(f"  {provider}: {status}")

    elif args.slm_command == "models":
        models = await client.list_models()
        print("Available Models")
        print("=" * 40)
        for provider, model_list in models.items():
            print(f"\n{provider}:")
            for model in model_list:
                print(f"  - {model}")

    elif args.slm_command == "pull":
        from ai.slm.client import OllamaClient
        from common.config import get_settings

        settings = get_settings()
        ollama = OllamaClient(settings)
        print(f"Pulling model: {args.model}")
        success = await ollama.pull_model(args.model)
        if success:
            print("Model pulled successfully!")
        else:
            print("Failed to pull model")
            sys.exit(1)


async def cmd_strategic(args):
    """Handle strategic commands"""
    from ai.strategic.meta_ai import StrategicMetaAI

    strategic_ai = StrategicMetaAI()

    if args.strategic_command == "review":
        print("Running strategic review...")
        review = await strategic_ai.run_immediate_review()

        print("\nStrategic Review Result")
        print("=" * 40)
        print(f"Review ID: {review.review_id}")
        print(f"Timestamp: {review.timestamp}")
        print(f"\nCurrent Metrics:")
        for k, v in review.current_metrics.items():
            print(f"  {k}: {v}")
        print(f"\nGoals Met:")
        print(f"  Ontology Coverage: {review.goals_met.ontology_coverage}")
        print(f"  MMO Accuracy: {review.goals_met.mmo_accuracy}")
        print(f"  AI Task Success: {review.goals_met.ai_task_success}")
        print(f"  Human Intervention: {review.goals_met.human_intervention}")
        print(f"  Ethical Flags: {review.goals_met.ethical_flags}")
        print(f"\nGaps Identified:")
        for gap in review.gaps:
            print(f"  - {gap}")
        print(f"\nProposed Actions:")
        for action in review.plan.actions:
            print(f"  - {action}")
        print(f"\nRationale: {review.plan.rationale}")
        print(f"Requires Human Approval: {review.plan.requires_human_approval}")

    elif args.strategic_command == "status":
        status = strategic_ai.get_oversight_status()
        print("Human Oversight Status")
        print("=" * 40)
        print(f"Pending Approvals: {status['pending_approvals']}")
        print(f"Unresolved Alerts: {status['unresolved_alerts']}")
        print(f"Halt Active: {status['halt_active']}")


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Route to command handlers
    if args.command == "start":
        asyncio.run(cmd_start(args))
    elif args.command == "stop":
        asyncio.run(cmd_stop(args))
    elif args.command == "status":
        asyncio.run(cmd_status(args))
    elif args.command == "health":
        asyncio.run(cmd_health(args))
    elif args.command == "services":
        cmd_services(args)
    elif args.command == "import":
        asyncio.run(cmd_import(args))
    elif args.command == "slm":
        if not args.slm_command:
            print("Usage: omnicore slm <status|models|pull>")
            sys.exit(1)
        asyncio.run(cmd_slm(args))
    elif args.command == "strategic":
        if not args.strategic_command:
            print("Usage: omnicore strategic <review|status>")
            sys.exit(1)
        asyncio.run(cmd_strategic(args))
    elif args.command == "rollback":
        print(f"Rollback to {args.version} (dry_run={args.dry_run})")
        print("Not implemented yet - use API endpoint")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
