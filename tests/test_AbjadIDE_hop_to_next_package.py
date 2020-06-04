import ide

abjad_ide = ide.AbjadIDE(test=True)


def test_AbjadIDE_hop_to_next_package_01():
    """
    In segments directory.
    """

    abjad_ide("red gg > > > q")
    transcript = abjad_ide.io.transcript
    assert transcript.titles == [
        "Abjad IDE : scores",
        "Red Score (2017)",
        "Red Score (2017) : segments",
        "Red Score (2017) : segments : _",
        "Red Score (2017) : segments : A",
        "Red Score (2017) : segments : B",
    ]


def test_AbjadIDE_hop_to_next_package_02():
    """
    In segment directory.
    """

    abjad_ide("red gg _ > > q")
    transcript = abjad_ide.io.transcript
    assert transcript.titles == [
        "Abjad IDE : scores",
        "Red Score (2017)",
        "Red Score (2017) : segments",
        "Red Score (2017) : segments : _",
        "Red Score (2017) : segments : A",
        "Red Score (2017) : segments : B",
    ]
