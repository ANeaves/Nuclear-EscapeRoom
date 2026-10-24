try:
    import typing
except ImportError:
    pass

class State(object):
    """Base State class for State Machines"""
    def __init__(self) -> None:
        pass

    @property
    def name(self):
        return ''

    def enter(self, machine):
        print(f"Entered State {self.name}")
        return self

    def exit(self, machine):
        print(f"Exited State {self.name}")
        pass

    def update(self, machine):
        pass


class StateMachine(object):
    """Basic State Machine class for handling state and transitions"""
    def __init__(self) -> None:
        self.state: typing.Union[State, None] = None
        self.states: dict[str, State] = {}

    def add_state(self, state: State):
        self.states[state.name] = state

    def go_to_state(self, state_name: str):
        if state_name not in self.states.keys():
            print(f"{state_name} not found as valid state")
            return
        if self.state:
            self.state.exit(self)
        self.state = self.states[state_name].enter(self)

    def update(self):
        """Run the Update method of the current state. May trigger a state change."""
        if self.state:
            self.state.update(self)
