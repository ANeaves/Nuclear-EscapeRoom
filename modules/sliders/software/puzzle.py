from typing import Literal, Union

PUZ_STATE = Literal["INIT", "RUN", "WON", "LOSS", "RESET"]


class Puzzle:
    """Base Puzzle Class, each puzzle module should extend this class"""

    def __init__(self, led_pin = 0, button_pin: Union[int , None] = None) -> None:
        self.state: PUZ_STATE = "INIT"

    def gen_solution(self):
        """Generate a solution to the puzzle. Must be extended by specific puzzle module"""
        pass

    def check_solution(self) -> bool:
        """Check that the solution from the user is correct"""
        return True

    