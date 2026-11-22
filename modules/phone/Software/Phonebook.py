"""Container File for Phonebook Dictionary"""

dial = "audio/dial_tone.mp3"
invalid = "audio/number_unavailable.mp3"
ringing = "audio/ringing.mp3"
poacher = "audio/poacher.mp3"
sam = "audio/sam.mp3"
zelda = "audio/zelda.mp3"
will = "audio/will.mp3"
penny = "audio/penny.mp3"
mex = "audio/mex.mp3"

class NumberResponse:

    def __init__(self, audio: "list[str]", code: int = 0 ) -> None:
        self.audio = [ringing] + audio
        self.code = code

Phonebook = {
    "01522960951": NumberResponse([poacher], 39715),
    "01154230998": NumberResponse([sam], 50890),
    "17112000341": NumberResponse([zelda], 19394),
    "01584531368": NumberResponse([will], 68017),
    "02079460972": NumberResponse([mex], 21657),
    "01282452716": NumberResponse([penny])
}