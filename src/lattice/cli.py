from __future__ import annotations

import argparse
import json
from pathlib import Path

from lattice.compiler import CompilerConfig, compile_dataset
from lattice.sources import DemoFetchConfig, run_demo_fetch
from lattice.utils import read_json


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lattice", description="Lattice data compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile", help="Compile raw sources into dataset views.")
    compile_parser.add_argument("--input", required=True, help="Input directory containing raw sources.")
    compile_parser.add_argument("--output", required=True, help="Output directory for compiled artifacts.")
    compile_parser.add_argument("--domain", required=True, help="Target domain label.")
    compile_parser.add_argument("--dataset-name", required=True, help="Dataset release name.")
    compile_parser.add_argument("--chunk-size", type=int, default=1200, help="Maximum characters per pretrain chunk.")

    fetch_parser = subparsers.add_parser("fetch-demo", help="Fetch a small real-source demo dataset.")
    fetch_parser.add_argument("--output", required=True, help="Directory for fetched raw source files.")
    fetch_parser.add_argument("--domain", default="materials", help="Target domain label.")
    fetch_parser.add_argument("--query", default="solid state battery electrolyte", help="Topic query.")
    fetch_parser.add_argument("--openalex-limit", type=int, default=3, help="Number of OpenAlex works to fetch.")
    fetch_parser.add_argument("--arxiv-limit", type=int, default=3, help="Number of arXiv entries to fetch.")
    fetch_parser.add_argument(
        "--compound",
        action="append",
        default=[],
        help="Compound name for PubChem lookup. Can be repeated.",
    )

    demo_parser = subparsers.add_parser("demo", help="Fetch a real-source demo and compile it.")
    demo_parser.add_argument("--raw-output", required=True, help="Directory for fetched raw source files.")
    demo_parser.add_argument("--compiled-output", required=True, help="Directory for compiled outputs.")
    demo_parser.add_argument("--domain", default="materials", help="Target domain label.")
    demo_parser.add_argument("--dataset-name", default="Lattice-Materials-RealDemo", help="Compiled dataset name.")
    demo_parser.add_argument("--query", default="solid state battery electrolyte", help="Topic query.")
    demo_parser.add_argument("--openalex-limit", type=int, default=3, help="Number of OpenAlex works to fetch.")
    demo_parser.add_argument("--arxiv-limit", type=int, default=3, help="Number of arXiv entries to fetch.")
    demo_parser.add_argument(
        "--compound",
        action="append",
        default=[],
        help="Compound name for PubChem lookup. Can be repeated.",
    )

    stats_parser = subparsers.add_parser("stats", help="Print summary stats from a compiled output.")
    stats_parser.add_argument("--path", required=True, help="Compiled output directory or manifest path.")
    return parser


def _handle_compile(args: argparse.Namespace) -> int:
    config = CompilerConfig(
        input_dir=args.input,
        output_dir=args.output,
        domain=args.domain,
        dataset_name=args.dataset_name,
        chunk_size=args.chunk_size,
    )
    manifest = compile_dataset(config)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def _compounds_or_default(compounds: list[str]) -> list[str]:
    if compounds:
        return compounds
    return ["lithium iron phosphate", "lithium cobalt oxide"]


def _handle_fetch_demo(args: argparse.Namespace) -> int:
    config = DemoFetchConfig(
        output_dir=args.output,
        domain=args.domain,
        query=args.query,
        openalex_limit=args.openalex_limit,
        arxiv_limit=args.arxiv_limit,
        compounds=_compounds_or_default(args.compound),
    )
    manifest = run_demo_fetch(config)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def _handle_demo(args: argparse.Namespace) -> int:
    fetch_config = DemoFetchConfig(
        output_dir=args.raw_output,
        domain=args.domain,
        query=args.query,
        openalex_limit=args.openalex_limit,
        arxiv_limit=args.arxiv_limit,
        compounds=_compounds_or_default(args.compound),
    )
    fetch_manifest = run_demo_fetch(fetch_config)
    compile_manifest = compile_dataset(
        CompilerConfig(
            input_dir=args.raw_output,
            output_dir=args.compiled_output,
            domain=args.domain,
            dataset_name=args.dataset_name,
        )
    )
    payload = {
        "fetch": fetch_manifest,
        "compile": compile_manifest,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def _handle_stats(args: argparse.Namespace) -> int:
    path = Path(args.path)
    manifest_path = path if path.name.endswith(".json") else path / "reports" / "manifest.json"
    manifest = read_json(manifest_path)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "compile":
        return _handle_compile(args)
    if args.command == "fetch-demo":
        return _handle_fetch_demo(args)
    if args.command == "demo":
        return _handle_demo(args)
    if args.command == "stats":
        return _handle_stats(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
