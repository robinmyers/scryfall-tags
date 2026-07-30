from main import main


def test_main_runs(capsys):
    main(["Lightning Bolt"])
    captured = capsys.readouterr()
    assert "Lightning Bolt" in captured.out


def test_dependencies_importable():
    import anthropic
    import dotenv
    import requests

    assert requests and anthropic and dotenv
