import ide

abjad_ide = ide.AbjadIDE(test=True)
scores = ide.configuration.test_scores_directory


def test_AbjadIDE_generate_music_ly_01():

    with ide.Test():
        target = ide.Path(
            scores, "red_score", "red_score", "builds", "letter-score", "music.ly"
        )
        target.remove()

        abjad_ide("red bb letter ggc mlg q")
        transcript = abjad_ide.io.transcript
        assert f"Generating {target.trim()} ..." in transcript
        # assert f'Removing {target.trim()} ...' in transcript
        assert f"Writing {target.trim()} ..." in transcript
        assert target.is_file()
        text = target.read_text()
        assert "Red Score (2017) for piano" in text
        assert r"\version" in text
        assert r"\language" in text
        assert '\n        \\include "_segments/segment-01.ly"' in text
        assert '\n        \\include "_segments/segment-02.ly"' in text
        assert '\n        \\include "_segments/segment-03.ly"' in text

        abjad_ide("red bb letter mlg q")
        transcript = abjad_ide.io.transcript
        assert f"Generating {target.trim()} ..." in transcript
        # assert f'Removing {target.trim()} ...' in transcript
        assert f"Writing {target.trim()} ..." in transcript
        assert target.is_file()
        text = target.read_text()
        assert "Red Score (2017) for piano" in text
        assert r"\version" in text
        assert r"\language" in text
        assert '\n        \\include "_segments/segment-01.ly"' in text
        assert '\n        \\include "_segments/segment-02.ly"' in text
        assert '\n        \\include "_segments/segment-03.ly"' in text


def test_AbjadIDE_generate_music_ly_02():
    """
    Comments out not-yet-extant segments.
    """

    with ide.Test():
        target = ide.Path(
            scores, "red_score", "red_score", "builds", "letter-score", "music.ly"
        )
        target.remove()

        segment_04 = target.segments / "04"
        segment_04.mkdir()

        abjad_ide("red bb letter ggc mlg q")
        transcript = abjad_ide.io.transcript
        assert f"Generating {target.trim()} ..." in transcript
        assert f"Writing {target.trim()} ..." in transcript
        assert target.is_file()
        text = target.read_text()
        assert "Red Score (2017) for piano" in text
        assert r"\version" in text
        assert r"\language" in text
        assert '\n        \\include "_segments/segment-01.ly"' in text
        assert '\n        \\include "_segments/segment-02.ly"' in text
        assert '\n        \\include "_segments/segment-03.ly"' in text
        assert '\n        %\\include "_segments/segment-04.ly"' in text
