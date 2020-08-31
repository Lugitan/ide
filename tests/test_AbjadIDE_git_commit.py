import ide

abjad_ide = ide.AbjadIDE(test=True)
scores = ide.configuration.test_scores_directory


def test_AbjadIDE_git_commit_01():
    """
    In score package directories.
    """

    abjad_ide("red ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript

    abjad_ide("red bb ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript

    abjad_ide("red dd ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript

    abjad_ide("red ee ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript

    abjad_ide("red gg ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript

    abjad_ide("red gg 02 ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript

    abjad_ide("red yy ci q")
    transcript = abjad_ide.io.transcript
    assert "> ci" in transcript


def test_AbjadIDE_git_commit_02():
    """
    In scores directory.
    """

    abjad_ide("ci Updated. q")
    transcript = abjad_ide.io.transcript
    assert "Commit message> Updated." in transcript
    for path in [
        ide.Path(scores, "red_score", "red_score"),
        ide.Path(scores, "blue_score", "blue_score"),
    ]:
        assert f"{path.wrapper} ..." in transcript
        assert "> ci" in transcript
