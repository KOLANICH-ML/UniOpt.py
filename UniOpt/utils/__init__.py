import shutil
import types
import typing
from pathlib import Path


class IterableModule(types.ModuleType):
	"""Just a module available for iteration"""

	__all__ = None

	def __iter__(self):
		for pn in self.__class__.__all__:
			yield getattr(self, pn)


def resolveAvailablePath(fileName: str):
	"""Searches a file in availability, like in PATH or in the folder."""
	p = shutil.which(fileName)
	if p:
		return Path(p).resolve().absolute()


def getEffectiveAttrForAClass(checkedProps: typing.Iterable[str], attrs: typing.Mapping[str, typing.Any], parents: typing.Iterable[type]) -> typing.Mapping[str, typing.Any]:
	effective = {pN: None for pN in checkedProps}

	for pN in checkedProps:
		if pN in attrs:
			effective[pN] = attrs[pN]
		else:
			for p in parents:
				if effective[pN] is None:
					if hasattr(p, pN):
						v = getattr(p, pN)
						if v:
							effective[pN] = v
							break
	return effective


def notInitializedFunction(*args, **kwargs):
	raise NotImplementedError("This function is used instead of None to make sanity checkers happy.")


def dummyFunction(*args, **kwargs):
	pass
