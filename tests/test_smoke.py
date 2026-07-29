from main import main


def test_main_runs(capsys):
    main()
    captured = capsys.readouterr()
    assert "scryfall-tags" in captured.out


def test_dependencies_importable():
    import anthropic
    import dotenv
    import requests

    assert requests and anthropic and dotenv
