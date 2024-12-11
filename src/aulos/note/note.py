from __future__ import annotations

import typing as t
from typing import TYPE_CHECKING

from .._core import AulosObject
from .._core.framework import coexist, inject
from .._core.utils import index
from ._base import BaseNote

if TYPE_CHECKING:
    from scale import Scale


class Note(BaseNote, AulosObject):

    @inject
    def __init__(
        self, identify: int | str, *, scale: t.Optional[Scale] = None, **kwargs
    ) -> None:
        super().__init__(**kwargs)

        if self.schema.is_notenumber(identify):
            notenames = self.schema.convert_notenumber_to_notenames(identify)
            self._notenumber: int = identify
            self._notenames: tuple[str] = notenames
            self._notename: t.Optional[str] = None
            self._scale: t.Optional[Scale] = None
            self.scale = scale

        elif self.schema.is_notename(identify):
            notenumber = self.schema.convert_notename_to_notenumber(identify)
            notenames = self.schema.convert_notenumber_to_notenames(notenumber)
            self._notenumber: int = notenumber
            self._notenames: tuple[str] = notenames
            self._notename: t.Optional[str] = identify
            self._scale: t.Optional[Scale] = None
            self.scale = scale

        else:
            raise ValueError()

    @property
    def notenumber(self) -> int:
        return self._notenumber

    @property
    def notename(self) -> t.Optional[str]:
        return self._notename

    @property
    def notenames(self) -> list[str]:
        return [n for n in self._notenames if n is not None]

    @property
    def scale(self) -> t.Optional[Scale]:
        return self._scale

    @notename.setter
    def notename(self, name: str):
        if self.is_notename(name) and name in self._notenames:
            self._notename = name

    @scale.setter
    @coexist
    def scale(self, scale: Scale):
        from ..scale import Mode, Scale

        if isinstance(scale, (Scale, Mode)):
            pitchclass = self.schema.convert_notenumber_to_pitchclass(self._notenumber)
            pitchclass = (pitchclass - scale.key.pitchclass) % self.schema.semitone
            if (idx := index(scale.positions, pitchclass)) is None:
                return
            acc, kacc = scale.accidentals[idx], scale.key.accsidentals[idx]
            self._notename = self.schema.convert_notenumber_to_notename(
                self._notenumber, acc + kacc
            )
            self._scale = scale

    @coexist
    def __eq__(self, other: int | BaseNote) -> bool:
        return int(self) == int(other)

    @coexist
    def __ne__(self, other: int | BaseNote) -> bool:
        return not self.__eq__(other)

    @coexist
    def __add__(self, other: int | BaseNote) -> Note:
        return Note(int(self) + int(other), scale=self.scale, setting=self.setting)

    @coexist
    def __sub__(self, other: int | BaseNote) -> Note:
        return Note(int(self) - int(other), scale=self.scale, setting=self.setting)

    def __int__(self):
        return self._notenumber

    def __str__(self) -> str:
        return self._notename or str(self._notenumber)

    def __repr__(self) -> str:
        return "<Note: {}>".format(self._notename or str(self.notenames))

    def is_notename(self, notename: t.Any) -> t.TypeGuard[str]:
        return self.schema.is_notename(notename)

    def is_notenumber(self, notenumber: t.Any) -> t.TypeGuard[int]:
        return self.schema.is_notenumber(notenumber)
