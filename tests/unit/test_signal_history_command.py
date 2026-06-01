from click.testing import CliRunner

from src.main import cli


def test_signal_history_command_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["signal-history", "--help"])
    assert result.exit_code == 0
    assert "Filter digest history by topic label." in result.output
