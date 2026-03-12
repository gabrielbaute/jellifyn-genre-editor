from enum import StrEnum

class ItemType(StrEnum):
    TRACK = "Track"
    ALBUM = "Album"
    ARTIST = "Artist"

    def __str__(self):
        return self.value