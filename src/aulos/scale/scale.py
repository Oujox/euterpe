import typing as t
from itertools import accumulate, starmap

from aulos._core import AulosObject
from aulos._core.utils import classproperty
from aulos.note import BaseKey, BasePitchClass

from .schemas import ScaleSchema


class Scale[KEY: BaseKey, PITCHCLASS: BasePitchClass](AulosObject[ScaleSchema]):
    """
    Scale class representing a musical scale.

    Attributes:
        Key (type[KEY]): The key type.
        PitchClass (type[PITCHCLASS]): The pitch class type.
        _intervals (t.ClassVar[tuple[int, ...]]): Intervals of the scale.
        _positions (t.ClassVar[tuple[int, ...]]): Positions of the scale.
        _key (KEY): The key of the scale.
        _signatures (tuple[int, ...]): Signatures of the scale.
    """

    Key: type[KEY]
    PitchClass: type[PITCHCLASS]
    _intervals: t.ClassVar[tuple[int, ...]]
    _positions: t.ClassVar[tuple[int, ...]]
    _key: KEY
    _signatures: tuple[int, ...]

    __slots__ = "_key", "_signatures"

    def __init__(self, key: str | KEY, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)

        if isinstance(key, str):
            self._key = self.Key(key, setting=self._setting)
            self._signatures = tuple(
                starmap(
                    lambda x, y: x + y,
                    zip(
                        self._key.signature,
                        self.schema.generate_scale_signatures(self._intervals),
                        strict=False,
                    ),
                ),
            )

        elif isinstance(key, BaseKey):
            self._key = key
            self._signatures = tuple(
                starmap(
                    lambda x, y: x + y,
                    zip(
                        self._key.signature,
                        self.schema.generate_scale_signatures(self._intervals),
                        strict=False,
                    ),
                ),
            )

        else:
            raise TypeError

    def __init_subclass__(
        cls,
        *,
        intervals: t.Sequence[int] | None = None,
        key: type[KEY] | None = None,
    ) -> None:
        if intervals is None or key is None:
            return
        schema = ScaleSchema(key.schema.pitchclass)
        super().__init_subclass__(schema=schema)
        cls.Key = key
        cls.PitchClass = key.PitchClass
        cls._intervals = tuple(intervals)
        cls._positions = tuple(accumulate((0,) + cls._intervals[:-1]))

    @property
    def key(self) -> KEY:
        return self._key

    @classproperty
    def intervals(self) -> tuple[int, ...]:
        return self._intervals

    @classproperty
    def positions(self) -> tuple[int, ...]:
        return self._positions

    @property
    def signatures(self) -> tuple[int, ...]:
        return self._signatures

    @property
    def components(self) -> tuple[PITCHCLASS, ...]:
        components = []
        root = self.PitchClass(self._key.keyname, scale=self, setting=self.setting)
        for pos in self.positions:
            pitchclass = (root + pos).pitchclass
            note = self.PitchClass(pitchclass, scale=self, setting=self.setting)
            components.append(note)
        return tuple(components)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Scale):
            return NotImplemented
        return self._intervals == other._intervals and self._key == other._key

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self._key}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self._key}>"
