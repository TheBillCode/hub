from re import match
from typing import Match


class Plantsudio:
    

    #define a list of keywords to populate influx with
    KEYWORDS = ["Temperature",
                "Humidity",
                "CarbonDioxide",
                "Power",
                "Weight",
                "Today"]

    @classmethod
    def get_keywords(cls, data):
        """Returns all key-value pairs where key is a KEYWORD using
        recursion to iterate through all dictionaries in dictionoary
        """
        pairs = {}
        for k,v in data.items():        
            if isinstance(v, dict):
                pairs = cls.get_keywords(v)
            else:   
                if k in cls.KEYWORDS:
                    pairs[k] = v
        return pairs

class Room:
    #constants
    FLOWERING_TEMPS = {"low":77, "high":82}
    WATER_RES_RAW = {"min":3236}

    _room_dict = {}

    def __init__(self, name):
        self._name = name
        self.climate = {}
        Room._room_dict[name] = self
        return

    def automation(cls, room):
        #coming soon
        return

    @classmethod
    def known_room(cls, room):
        """Returns True if room already known to plantstudio

        Args:
            room (str): Name of room

        Returns:
            [bool]: True if room already found.
        """
        if room in cls._room_dict:
            return True
        else:
            return False

    @classmethod
    def update_room(cls, room, pairs):
        """Updates room dictionary with new values

        Args:
            room (str): Name of room
            pairs (dict): new sensor values for room
        """
        for k in pairs:
            cls._room_dict[room].climate[k] = pairs[k]
        print("----" + room + " Room Updated----")
        print(cls._room_dict[room].climate)
        return

