from framework.runners.cli_runner import CliRunner


def main() -> None:
    runner = CliRunner()
    parser = runner.build_parser()
    args = parser.parse_args()
    result = runner.run(args)

    print("\n=== AutoTest Pro Execution Result ===")
    print(f"Status: {result.status}")
    print(f"Browser: {result.browser}")
    print(f"Environment: {result.environment}")
    print(f"Duration: {result.duration_seconds} seconds")
    print(f"Message: {result.message}")
    print("\nGenerated reports:")
    for report_type, path in result.reports.items():
        if path:
            print(f"- {report_type.upper()}: {path}")

    if result.status != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
