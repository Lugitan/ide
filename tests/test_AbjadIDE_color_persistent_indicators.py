import ide

abjad_ide = ide.AbjadIDE(test=True)
scores = ide.configuration.test_scores_directory


def test_AbjadIDE_color_persistent_indicators_01():
    """
    In build directory.
    """

    with ide.Test():

        build = ide.Path(scores, "green_score", "green_score", "builds", "arch-a-score")
        path = build / "_segments" / "segment--.ly"

        abjad_ide("gre bb arch-a-score ggc q")
        assert path.is_file()

        abjad_ide("gre bb arch-a-score color persistent q")
        lines = abjad_ide.io.transcript.lines
        for line in [
            "Coloring persistent indicators ...",
            " Found 26 persistent indicator color expression tags ...",
            " Activating 26 persistent indicator color expression tags ...",
            " Found 1 persistent indicator color suppression tag ...",
            " Deactivating 1 persistent indicator color suppression tag ...",
        ]:
            assert line in lines

        abjad_ide("gre bb arch-a-score uncolor persistent q")
        lines = abjad_ide.io.transcript.lines
        for line in [
            "Uncoloring persistent indicators ...",
            " Found 26 persistent indicator color expression tags ...",
            " Deactivating 26 persistent indicator color expression tags ...",
            " Found 1 persistent indicator color suppression tag ...",
            " Activating 1 persistent indicator color suppression tag ...",
        ]:
            assert line in lines

        abjad_ide("gre bb arch-a-score color persistent q")
        lines = abjad_ide.io.transcript.lines
        for line in [
            "Coloring persistent indicators ...",
            " Found 26 persistent indicator color expression tags ...",
            " Activating 26 persistent indicator color expression tags ...",
            " Found 1 persistent indicator color suppression tag ...",
            " Deactivating 1 persistent indicator color suppression tag ...",
        ]:
            assert line in lines


def test_AbjadIDE_color_persistent_indicators_02():
    """
    In segment directory.
    """

    with ide.Test():

        path = ide.Path(
            scores, "green_score", "green_score", "segments", "_", "illustration.ly"
        )
        assert path.is_file()

        abjad_ide("gre _ color persistent q")
        lines = abjad_ide.io.transcript.lines
        for line in [
            "Coloring persistent indicators ...",
            " Found 30 persistent indicator color expression tags ...",
            " Activating 4 persistent indicator color expression tags ...",
            " Skipping 26 (active) persistent indicator color expression tags ...",
            " Found 1 persistent indicator color suppression tag ...",
            " Skipping 1 (inactive) persistent indicator color suppression tag ...",
        ]:
            assert line in lines

        abjad_ide("gre _ uncolor persistent q")
        lines = abjad_ide.io.transcript.lines
        for line in [
            "Uncoloring persistent indicators ...",
            " Found 26 persistent indicator color expression tags ...",
            " Deactivating 26 persistent indicator color expression tags ...",
            " Found 1 persistent indicator color suppression tag ...",
            " Activating 1 persistent indicator color suppression tag ...",
        ]:
            assert line in lines

        abjad_ide("gre _ color persistent q")
        lines = abjad_ide.io.transcript.lines
        for line in [
            "Coloring persistent indicators ...",
            " Found 26 persistent indicator color expression tags ...",
            " Activating 26 persistent indicator color expression tags ...",
            " Found 1 persistent indicator color suppression tag ...",
            " Deactivating 1 persistent indicator color suppression tag ...",
        ]:
            assert line in lines
