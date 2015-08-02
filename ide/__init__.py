# -*- encoding: utf-8 -*-
'''Installing the Abjad IDE.

To install the Abjad IDE:

    1. verify the Abjad IDE directories.
    2. add abjad_ide/scr/ to your PATH.
    3. create a scores/ directory.
    4. start and stop the Abjad IDE.
    5. run pytest.
    6. build the Abjad IDE API.
    7. run doctest.

1. Verify the Abjad IDE directories. The following 7 directories should appear
on your filesystem after checkout:

    boilerplate/
    docs/
    etc/
    idetools/
    scores/
    scr/
    test/

2. Add the abjad_ide/scr/ directory to your PATH. This tells your shell
where the start-abjad-idetools script is housed:

    export PATH=$ABJAD/ide/scr:$PATH

3. Create a scores directory. You can do this anywhere on your filesystem you
wish. Then create a SCORES environment variable in your profile. Set the scores
environment variable to your scores directory:

    export SCORES=$DOCUMENTS/scores

4. Start and stop the Abjad IDE. Type start-abjad-idetools at the commandline.
The Abjad IDE should start. What you see here probably won't be very
interesting because you won't yet have any scores created on your system. But
you should see three Abjad example scores as well as three or four menu
options. The menu options allow you to manage scores, segments, materials and
other assets. If the shell can't find start-abjad-idetools then make sure you
added the scroremanager/scr/ directory to your PATH. After the Abjad IDE starts
correctly enter 'q' to quit the Abjad IDE.

5. Run pytest against the abjad_ide directory. Fix or report tests that
break.

6. Build the Abjad IDE API. Run 'avj api -S' to do this.

7. Run doctest on the abjad_ide/ directory.  Run 'ajv doctest' in
abjad_ide/ directory to do this. You're ready to use the Abjad IDE when
all tests pass.
'''

from ide.tools import idetools
configuration = idetools.AbjadIDEConfiguration()
configuration._add_example_score_to_sys_path()
del(configuration)
del(idetools)