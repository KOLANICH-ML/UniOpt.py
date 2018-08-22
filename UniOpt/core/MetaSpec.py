import re

__all__ = ("IntegerMetaMap", "ScalarMetaMap", "MSpec")
import typing
from collections import OrderedDict
from enum import IntEnum
from functools import lru_cache
from warnings import warn

from .ArraySpec import ArraySpec
from .Spec import *
from .SpecNoIntegers import IntegerMetaMap
from .SpecNoScalars import ScalarMetaMap


def specClassNameGenerator(*, isArray: bool = False, integerMode=None, scalarMode=None, isDummy: bool = False):
	name = []
	if isDummy:
		name.append("Dummy")
	if isArray:
		name.append("Array")

	name.append("Spec")

	if scalarMode:
		name.append("NoScalars" + ScalarMetaMap._classToNamePartMapping[scalarMode])

	if integerMode:
		name.append(IntegerMetaMap._classToNamePartMapping[integerMode] + "Integers")

	return "".join(name)


nameRx = re.compile("^(Dummy)?(Array)?Spec(?:NoScalars(Dumb|Categorical))?(?:(To|No)Integers)?$")


def parseName(name: str) -> typing.Mapping[str, typing.Any]:
	names = ("isDummy", "isArray", "scalarMode", "integerMode")
	res = dict(zip(names, nameRx.match(name).groups()))
	res["isDummy"] = bool(res["isDummy"])
	res["isArray"] = bool(res["isArray"])
	res["scalarMode"] = ScalarMetaMap._namePartToClassMapping[res["scalarMode"]]
	res["integerMode"] = IntegerMetaMap._namePartToClassMapping[res["integerMode"]]
	return res


@lru_cache(maxsize=None, typed=True)
def MSpec(*name: typing.Optional[typing.Tuple[str]], isArray: bool = False, integerMode=None, scalarMode=None, isDummy: bool = False, **kwargs):
	"""A class choosing the right sequence of inheritance of mixins depending on traits the spec class must have"""
	if name:
		assert len(name) == 1
		assert isinstance(name[0], str)
		return MSpec(**parseName(name[0]), name=name[0])
	else:
		superclasses = []
		if isDummy:
			superclasses.append(DummySpec)

		if isArray:
			superclasses.append(ArraySpec)

		if integerMode:
			superclasses.append(integerMode)

		if scalarMode:
			superclasses.append(scalarMode)

		if not superclasses:
			superclasses.append(Spec)

		if len(superclasses) == 1:
			#warn("Use " + superclasses[0].__name__ + " directly")
			return superclasses[0]

		if "name" in kwargs:
			name = kwargs["name"]
		else:
			name = specClassNameGenerator(isArray=isArray, integerMode=integerMode, scalarMode=scalarMode, isDummy=isDummy)

		return type(name, tuple(superclasses), {})
