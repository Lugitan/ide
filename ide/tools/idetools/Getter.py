# -*- encoding: utf-8 -*-
import re
import functools
import numbers
from abjad import *
from ide.tools.idetools.Controller import Controller


class Getter(Controller):
    r'''Getter.
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_all_prompts_are_done',
        '_allow_none',
        '_capitalize_prompts',
        '_current_prompt_is_done',
        '_evaluated_input',
        '_include_newlines',
        '_include_chevron',
        '_number_prompts',
        '_prompt_character',
        '_prompt_index',
        '_messages',
        '_prompts',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        session=None,
        allow_none=False,
        capitalize_prompts=True,
        include_chevron=True,
        include_newlines=False,
        number_prompts=False,
        prompt_character=']>',
        ):
        Controller.__init__(self, session=session)
        self._prompts = []
        self._allow_none = allow_none
        self._capitalize_prompts = capitalize_prompts
        self._include_chevron = include_chevron
        self._include_newlines = include_newlines
        self._number_prompts = number_prompts
        self._prompt_character = prompt_character

    ### SPECIAL METHODS ###

    def __format__(self, format_specification=''):
        r'''Gets format of user input getter.

        Returns string.
        '''
        return repr(self)

    def __len__(self):
        r'''Gets number of prompts in user input getter menu.

        Returns nonnegative integer.
        '''
        return len(self.prompts)

    def __repr__(self):
        r'''Gets interpreter representation of user input getter.

        Returns string.
        '''
        return '<{} ({})>'.format(type(self).__name__, len(self))

    def __str__(self):
        r'''Gets string representation of user input getter.

        Returns string.
        '''
        return repr(self)

    ### PRIVATE PROPERTIES ###

    @property
    def _abjad_import_statement(self):
        return 'from abjad import *'

    @property
    def _current_prompt(self):
        return self.prompts[self._prompt_index]

    ### PRIVATE METHODS ###

    def _evaluate_input(self, input_, namespace):
        section = self._current_prompt.target_menu_section
        setup_statements = self._current_prompt.setup_statements
        if 'evaluated_input' in namespace:
            del(namespace['evaluated_input'])
        if self.allow_none and input_ in ('', 'None'):
            namespace['evaluated_input'] = None
        elif section is not None:
            evaluated_input = section._argument_range_string_to_numbers(
                input_)
            if (1 < len(evaluated_input) and
                self._current_prompt.disallow_range):
                evaluated_input = None
            namespace['evaluated_input'] = evaluated_input
        elif setup_statements:
            for setup_statement in self._current_prompt.setup_statements:
                try:
                    command = setup_statement.format(input_)
                    exec(command, namespace, namespace)
                    continue
                except (NameError, SyntaxError):
                    pass
                try:
                    command = setup_statement.format(repr(input_))
                    exec(command, namespace, namespace)
                except ValueError:
                    self.display_help()
        else:
            try:
                namespace['evaluated_input'] = eval(
                    input_, namespace, namespace)
            except (NameError, SyntaxError):
                namespace['evaluated_input'] = input_
        if not 'evaluated_input' in namespace:
            return
        if not self._validate_evaluated_input(namespace['evaluated_input']):
            self.display_help()
            return
        self._evaluated_input.append(namespace['evaluated_input'])
        self._prompt_index += 1
        self._current_prompt_is_done = True

    def _indent_and_number_message(self, message):
        if self.number_prompts:
            prompt_number = self._prompt_index + 1
            message = '({}/{}) {}'.format(
                prompt_number, len(self), message)
        return message

    def _load_message(self):
        message = self._current_prompt.message
        if self.capitalize_prompts:
            message = stringtools.capitalize_start(message)
        self._messages.append(message)

    def _make_prompt(
        self,
        spaced_attribute_name,
        disallow_range=False,
        help_template=None,
        help_template_arguments=None,
        include_chevron=True,
        setup_statements=None,
        target_menu_section=None,
        validation_function=None,
        ):
        from ide.tools import idetools
        prompt = idetools.Prompt(
            disallow_range=disallow_range,
            help_template=help_template,
            help_template_arguments=help_template_arguments,
            include_chevron=include_chevron,
            message=spaced_attribute_name,
            setup_statements=setup_statements,
            target_menu_section=target_menu_section,
            validation_function=validation_function,
            )
        self._prompts.append(prompt)

    def _move_to_previous_prompt(self):
        self._evaluated_input.pop()
        self._prompt_index = self._prompt_index - 1

    def _present_prompt(self, include_chevron=True):
        self._load_message()
        self._current_prompt_is_done = False
        namespace = {}
        while not self._current_prompt_is_done:
            message = self._messages[-1]
            message = self._indent_and_number_message(message)
            include_chevron = self._current_prompt.include_chevron
            input_ = self._io_manager._handle_input(
                message,
                include_chevron=include_chevron,
                include_newline=self.include_newlines,
                prompt_character=self.prompt_character,
                capitalize_prompt=self.capitalize_prompts,
                )
            if input_ is None:
                self._prompt_index += 1
                break
            elif input_ == '?':
                self.display_help()
                continue
            elif input_ in self._command_to_method:
                self._command_to_method[input_]()
            assert isinstance(input_, str), repr(input_)
            directive = input_
            if self._session.is_backtracking:
                self._current_prompt_is_done = True
                self._all_prompts_are_done = True
                self._session._pending_redraw = True
            elif directive is None:
                continue
            elif directive == 'help':
                self.display_help()
            elif directive == 'previous':
                self._move_to_previous_prompt()
                break
            elif directive == 'skip':
                break
            elif isinstance(directive, str):
                self._evaluate_input(directive, namespace)
            else:
                self._io_manager._display_not_yet_implemented()

    def _present_prompts(self, include_chevron=True):
        self._prompt_index = 0
        self._messages = []
        self._evaluated_input = []
        self._all_prompts_are_done = False
        while (self._prompt_index < len(self) and
            not self._all_prompts_are_done):
            self._present_prompt(include_chevron=include_chevron)

    def _run(self, clear_terminal=False, title=False):
        with self._io_manager._controller(
            consume_local_backtrack=True,
            controller=self,
            is_in_confirmation_environment=True,
            ):
            self._present_prompts(include_chevron=self._include_chevron)
            if len(self._evaluated_input) == 1:
                result = self._evaluated_input[0]
            else:
                result = self._evaluated_input[:]
            if result == []:
                result = None
            return result

    def _validate_evaluated_input(self, evaluated_input):
        if evaluated_input is None and self.allow_none:
            return True
        validation_function = self._current_prompt.validation_function
        try:
            return validation_function(evaluated_input)
        except TypeError:
            return False

    ### PUBLIC PROPERTIES ###

    @property
    def allow_none(self):
        r'''Is true when user input getter allows none.
        Otherwise false.

        Returns boolean.
        '''
        return self._allow_none

    @property
    def capitalize_prompts(self):
        r'''Is true when user input getter capitalizes prompts.
        Otherwise false.

        Returns boolean.
        '''
        return self._capitalize_prompts


    @property
    def include_chevron(self):
        r'''Is true when user input getter incldues chevron.
        Otherwise false.

        Returns boolean.
        '''
        return self._include_chevron

    @property
    def include_newlines(self):
        r'''Is true when user input getter incldues newlines.
        Otherwise false.

        Returns boolean.
        '''
        return self._include_newlines

    @property
    def number_prompts(self):
        r'''Is true when user input getter numbers prompts.
        Otherwise false.

        Returns boolean.
        '''
        return self._number_prompts

    @property
    def prompt_character(self):
        r'''Gets user input getter prompt character.

        Returns string.
        '''
        return self._prompt_character

    @property
    def prompts(self):
        r'''Gets user input getter prompts.

        Returns list of prompts.
        '''
        return self._prompts

    ### PUBLIC METHODS ###

    def append_dash_case_file_name(
        self,
        spaced_attribute_name,
        ):
        r'''Appends dash case file name.

        Returns prompt.
        '''
        help_template = 'value must be dash case file name.'
        self._make_prompt(
            spaced_attribute_name,
            help_template=help_template,
            validation_function=stringtools.is_dash_case_file_name,
            )

    def append_integer(
        self,
        spaced_attribute_name,
        ):
        r'''Appends integer.

        Returns prompt.
        '''
        help_template = 'value must be integer.'
        self._make_prompt(
            spaced_attribute_name,
            validation_function=Getter.is_integer,
            help_template=help_template,
            )

    def append_integer_in_range(
        self,
        spaced_attribute_name,
        start=None,
        stop=None,
        allow_none=False,
        ):
        r'''Appends integer in range.

        Returns prompt.
        '''
        validation_function = functools.partial(
            Getter.is_integer_in_range,
            start=start,
            stop=stop,
            allow_none=allow_none,
            )
        help_template = 'value must be integer between {} and {}, inclusive.'
        self._make_prompt(
            spaced_attribute_name,
            help_template=help_template,
            validation_function=validation_function,
            help_template_arguments=(start, stop),
            )

    def append_integers(
        self,
        spaced_attribute_name,
        ):
        r'''Appends integers.

        Returns prompt.
        '''
        help_template = 'value must be tuple of integers.'
        function = lambda x: all(Getter.is_integer(y) for y in x)
        self._make_prompt(
            spaced_attribute_name,
            validation_function=function,
            help_template=help_template,
            )

    def append_markup(
        self,
        spaced_attribute_name,
        ):
        r'''Appends markup.

        Returns prompt.
        '''
        help_template = 'value must be markup.'
        setup_statements = []
        setup_statements.append(self._abjad_import_statement)
        statement = 'evaluated_input = markuptools.Markup({})'
        setup_statements.append(statement)
        self._make_prompt(
            spaced_attribute_name,
            validation_function=Getter.is_markup,
            help_template=help_template,
            setup_statements=setup_statements,
            )

    def append_menu_section_item(
        self,
        spaced_attribute_name,
        target_menu_section,
        ):
        r'''Appends menu section item.

        Returns prompt.
        '''
        help_template = 'value must be menu section item.'
        self._make_prompt(
            spaced_attribute_name,
            validation_function=Getter.is_list,
            help_template=help_template,
            target_menu_section=target_menu_section,
            disallow_range=True,
            )

    def append_menu_section_range(
        self,
        spaced_attribute_name,
        target_menu_section,
        ):
        r'''Appends menu section range.

        Returns prompt.
        '''
        help_template = 'value must be argument range.'
        self._make_prompt(
            spaced_attribute_name,
            validation_function=Getter.is_list,
            help_template=help_template,
            target_menu_section=target_menu_section,
            )

    def append_named_pitch(
        self,
        spaced_attribute_name,
        ):
        r'''Appends named pitch.

        Returns prompt.
        '''
        help_template = 'value must be named pitch.'
        setup_statements = []
        setup_statements.append(self._abjad_import_statement)
        string = 'evaluated_input = pitchtools.NamedPitch({!r})'
        setup_statements.append(string)
        self._make_prompt(
            spaced_attribute_name,
            help_template=help_template,
            validation_function=Getter.is_named_pitch,
            setup_statements=setup_statements,
            )

    def append_string(
        self,
        spaced_attribute_name,
        allow_empty=True,
        ):
        r'''Appends string.

        Returns prompt.
        '''
        if allow_empty:
            validation_function = Getter.is_string
            help_template = 'value must be string.'
        else:
            validation_function = Getter.is_nonempty_string
            help_template = 'value must be nonempty string.'
        self._make_prompt(
            spaced_attribute_name,
            validation_function=validation_function,
            help_template=help_template,
            )

    def append_string_or_none(
        self,
        spaced_attribute_name,
        ):
        r'''Appends string or none.

        Returns prompt.
        '''
        help_template = 'value must be string or none.'
        self._make_prompt(
            spaced_attribute_name,
            validation_function=Getter.is_string_or_none,
            help_template=help_template,
            )

    def append_yes_no_string(
        self,
        spaced_attribute_name,
        include_chevron=False,
        ):
        r'''Appends yes / no string.

        Returns prompt.
        '''
        help_template = "value for '{}' must be 'y' or 'n'."
        self._make_prompt(
            spaced_attribute_name,
            validation_function=Getter.is_yes_no_string,
            help_template=help_template,
            include_chevron=include_chevron,
            )

    def display_help(self):
        r'''Displays help.

        Returns none.
        '''
        lines = []
        lines.append(self._current_prompt.help_string)
        lines.append('')
        self._io_manager._display(lines)

    @staticmethod
    def is_boolean(expr):
        r'''Predicate.
        '''
        return isinstance(expr, bool)

    @staticmethod
    def is_identifier(expr, allow_spaces=False):
        r'''Predicate.
        '''
        if not isinstance(expr, str):
            return False
        if len(expr) < 1:
            return False
        if expr[0] in '0123456789':
            return False
        for _ in expr:
            if allow_spaces:
                if not (_.isalnum() or _ == '_' or _ == ' '):
                    return False
            else:
                if not (_.isalnum() or _ == '_'):
                    return False
        return True

    @staticmethod
    def is_integer(expr):
        r'''Predicate.
        '''
        return isinstance(expr, int)

    @staticmethod
    def is_integer_in_range(expr, start=None, stop=None, allow_none=False):
        r'''Predicate.
        '''
        if expr is None and allow_none:
            return True
        if Getter.is_integer(expr) and \
            (start is None or start <= expr) and \
            (stop is None or expr <= stop):
            return True
        return False

    @staticmethod
    def is_integer_or_none(expr):
        r'''Predicate.
        '''
        return expr is None or is_integer(expr)

    @staticmethod
    def is_list(expr):
        r'''Predicate.
        '''
        return isinstance(expr, list)

    @staticmethod
    def is_markup(expr):
        r'''Predicate.
        '''
        return isinstance(expr, markuptools.Markup)

    @staticmethod
    def is_named_pitch(expr):
        r'''Predicate.
        '''
        return isinstance(expr, NamedPitch)

    @staticmethod
    def is_nonempty_string(expr):
        r'''Predicate.
        '''
        return isinstance(expr, str) and bool(expr)

    @staticmethod
    def is_page_layout_unit(expr):
        r'''Predicate.
        '''
        return expr in ('in', 'mm', 'cm', 'pt', 'pica')

    @staticmethod
    def is_paper_dimension_string(expr):
        r'''Predicate.
        '''
        if not isinstance(expr, str):
            return False
        parts = expr.split()
        if not len(parts) == 4:
            return False
        width, x, height, units = parts
        try:
            float(width) 
        except ValueError:
            return False
        try:
            float(height) 
        except ValueError:
            return False
        if not x == 'x':
            return False
        if not Getter.is_page_layout_unit(units):
            return False
        return True

    @staticmethod
    def is_string(expr):
        r'''Predicate.
        '''
        return isinstance(expr, str)

    @staticmethod
    def is_string_or_none(expr):
        r'''Predicate.
        '''
        return isinstance(expr, (str, type(None)))

    @staticmethod
    def is_yes_no_string(expr):
        r'''Predicate.
        '''
        return 'yes'.startswith(expr.lower()) or 'no'.startswith(expr.lower())