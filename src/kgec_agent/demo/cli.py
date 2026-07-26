"""Command-line entry point for deterministic reviewer replay."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from kgec_agent.agent.replay import available_scenarios, replay_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m kgec_agent.demo",
        description="Replay the KGEC-Agent reviewer scenarios without network or live inference.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    replay = subparsers.add_parser("replay", help="run one deterministic scenario")
    replay.add_argument("--scenario", required=True, choices=available_scenarios())
    replay.add_argument("--output-dir", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = replay_scenario(args.scenario, args.output_dir)
    except Exception as exc:
        print(f"REPLAY_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"SCENARIO={result.run.scenario_id}")
    print(f"FINAL_DECISION={result.run.final_decision}")
    print(f"DESTINATION={result.run.destination}")
    print(f"RUN_HASH={result.run.content_hash}")
    for name in ("json", "csv", "turtle", "markdown"):
        print(f"{name.upper()}={result.export_paths[name]}")
    return 0
