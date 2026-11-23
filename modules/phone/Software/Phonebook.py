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

    def __init__(self, audio: "list[str]", code: int = 0, network: list[str] = [] ) -> None:
        self.audio = [ringing] + audio
        self.code = code
        self.network = network

Phonebook = {
    "01522960951": NumberResponse([poacher], 39715, ["DZM905-I", "WRATAV-A", "KLP482-E", "KLM124-R", "DZN302-K", "WRB211-M"]),
    "01154230998": NumberResponse([sam],     50890, ["FXAHAS-E", "TRO731-A", "XEN905-I", "FQA124-K", "TXO211-M", "FAN302-R"]),
    "17112000341": NumberResponse([zelda],   19394, ["VMP527-R", "JQF456-K", "DZW638-T", "BRK234-T", "ZMP315-R", "GHT402-K"]),
    "01584531368": NumberResponse([will],    68017, ["BRKTVM-P", "ZMPQHL-R", "GHTKDW-T", "VEXMRK-S", "KURPZN-B", "JAMWFT-K"]),
    "02079460972": NumberResponse([mex],     21657, ["BRA234-T", "ZIP305-R", "GHO402-K", "VEX223-M", "KUR304-P", "JAM502-Z"]),
    "01282452716": NumberResponse([penny])
}