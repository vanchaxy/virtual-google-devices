from inflection import underscore


class BaseTrait:
    def __init__(self, attributes, states):
        self.attributes = attributes
        self.states = states

    def process_command(self, command, params):
        command_func_name = underscore(command.split('.')[-1])
        command_func = getattr(self, command_func_name)

        params = {underscore(k): v for k, v in params.items()}
        command_func(**params)

        return self.states
