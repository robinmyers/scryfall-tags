from main import main


def test_main_runs(capsys):
    main()
    captured = capsys.readouterr()
    assert "scryfall-tags" in captured.out
