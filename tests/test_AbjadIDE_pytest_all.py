import ide

abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_pytest_all_01():
    """
    In contents directory.
    """

    abjad_ide("red ++ q")
    transcript = abjad_ide.io.transcript
    assert "Matching '++' to 1 file ..." in transcript

    abjad_ide("red ++def q")
    transcript = abjad_ide.io.transcript
    assert "Matching '++def' to 0 files ..." in transcript

    abjad_ide("red ++rpc q")
    transcript = abjad_ide.io.transcript
    assert "Matching '++rpc' to 0 files ..." in transcript

    abjad_ide("red ++A q")
    transcript = abjad_ide.io.transcript
    assert "Matching '++A' to 0 files ..." in transcript

    abjad_ide("red ++ST q")
    transcript = abjad_ide.io.transcript
    assert "Matching '++ST' to 0 files ..." in transcript


def test_AbjadIDE_pytest_all_04():
    """
    Handles empty input and junk input.
    """

    abjad_ide("++asdf q")
    transcript = abjad_ide.io.transcript
    assert "Matching '++asdf' to 0 files ..." in transcript
