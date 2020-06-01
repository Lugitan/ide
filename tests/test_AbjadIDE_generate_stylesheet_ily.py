import ide

abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_generate_stylesheet_ily_01():

    with ide.Test():
        source = ide.Path("boilerplate", "stylesheet.ily")
        text = source.read_text()
        assert "paper_size" in text
        assert '"letter"' not in text
        target = ide.Path("blue_score", "builds", "letter-score")
        target /= "stylesheet.ily"
        target.remove()

        abjad_ide("blu %letter ssig q")
        transcript = abjad_ide.io.transcript
        assert "Generating stylesheet ..." in transcript
        assert f"Removing {target.trim()} ..." not in transcript
        assert f"Writing {target.trim()} ..." in transcript
        assert target.is_file()
        text = target.read_text()
        assert "paper_size" not in text
        assert '"letter"' in text

        abjad_ide("blu %letter ssig q")
        transcript = abjad_ide.io.transcript
        assert "Generating stylesheet ..." in transcript
        assert f"Removing {target.trim()} ..." in transcript
        assert f"Writing {target.trim()} ..." in transcript
        assert target.is_file()
        text = target.read_text()
        assert "paper_size" not in text
        assert '"letter"' in text