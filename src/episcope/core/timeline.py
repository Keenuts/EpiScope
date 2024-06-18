from enum import Enum
import json
from typing import Self, Optional
from dataclasses import dataclass

from episcope.core import Symptom, Criteria

class BlockType(Enum):
    SPACER = 0,
    SYMPTOM = 1

@dataclass
class TimelineItem:
    identifier : int
    symptom : Symptom
    criterias : list[Criteria]
    start : int
    duration : int

class Timeline():
    def __init__(self : Self) -> None:
        self._symptoms : dict[int, TimelineItem] = {}
        self._timeline : list[int] = []
        self._next_id : int = 1

    def _allocateId(self : Self) -> int:
        identifier = self._next_id
        self._next_id += 1
        return identifier

    def _updateTimeline(self : Self):
        self._timeline = sorted(self._timeline, key=lambda x : self._symptoms[x].start)

    def getDuration(self : Self) -> int:
        if len(self._timeline) == 0:
            return 0
        item = self._symptoms[self._timeline[-1]]
        return item.start + item.duration

    def getSymptoms(self : Self) -> list[TimelineItem]:
        output = []
        for identifier in self._timeline:
            item = self._symptoms[identifier]
            output.append(item)
        return output

    def addSymptom(self : Self, symptom : Symptom, criterias : list[Criteria], start : int, end : int) -> int:
        identifier = self._allocateId()
        self._symptoms[identifier] = TimelineItem(identifier, symptom, criterias, start, end - start)
        self._timeline.append(identifier)
        self._updateTimeline()
        return identifier

    def updateSymptom(self : Self,
                      identifier : int,
                      symptom : Optional[Symptom] = None,
                      start : Optional[int] = None,
                      end : Optional[int] = None) -> bool:
        if symptom is not None:
            self._symptoms[identifier].symptom = symptom

        old_start = self._symptoms[identifier].start
        old_end = old_start + self._symptoms[identifier].duration

        if start is not None:
            self._symptoms[identifier].start = start
            self._symptoms[identifier].duration = old_end - start

        start = self._symptoms[identifier].start
        if end is not None:
            self._symptoms[identifier].duration = end - start

        self._updateTimeline()
        return True

    def getItem(self : Self, identifier : int) -> Optional[TimelineItem]:
        if identifier not in self._symptoms:
            return None
        return self._symptoms[identifier]

    def getPreviousSymptom(self : Self, identifier : int) -> Optional[TimelineItem]:
        for i in range(len(self._timeline)):
            if self._timeline[i] == identifier:
                return self.getItem(self._timeline[i - 1]) if i > 0 else None
        return None

    def getNextSymptom(self : Self, identifier : int) -> Optional[TimelineItem]:
        for i in range(len(self._timeline)):
            if self._timeline[i] == identifier:
                return self.getItem(self._timeline[i + 1]) if i + 1 < len(self._timeline) else None
        return None

    def removeSymptom(self : Self, identifier : int) -> None:
        del self._symptoms[identifier]
        self._timeline.remove(identifier)

    def toJSON(self : Self) -> str:
        output = []
        for item in self.getSymptoms():
            output.append({
                'name': item.symptom.path(),
                'criterias': item.criterias,
                'start': int(item.start),
                'end': int(item.start + item.duration)
            })
        return json.dumps(output, indent=4)