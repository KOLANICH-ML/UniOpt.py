__all__ = ("PointsStorage", "DummyStorage", "MemoryStorage", "SQLiteStorage")
import heapq
from itertools import islice

from lazily.Cache import JSONCache

from ..imports import *
from . import LossT, Point, PointsSequenceT


def keyFunc(p):
	return p[1]


class PointsStorage:
	"""Used to store points - pairs (point in hyperparams space in form of dict, loss in that point (mean, variance))"""

	__slots__ = ()

	def __init__(self) -> None:
		raise NotImplementedError()

	def append(self, params, loss):
		raise NotImplementedError()

	def __iter__(self):
		raise NotImplementedError()

	def __len__(self):
		raise NotImplementedError()

	def __enter__(self):
		raise NotImplementedError()

	def prepare(self, n: int = None, requireSorted: bool = True) -> typing.Tuple[PointsSequenceT, int]:
		"""Prepares cached points: loads them and returns their sequence and the best point index."""
		if n is not None:
			if requireSorted:
				res = nlargest(n, self, key=keyFunc)
			else:
				res = list(islice(self, 0, n))
		else:
			if requireSorted:
				res = sorted(self, key=keyFunc)
			else:
				res = list(self)
		return res, (0 if len(res) else None)


class DummyStorage(PointsStorage):
	def __init__(self) -> None:
		pass

	def append(self, params: dict, loss: LossT) -> None:
		pass

	def __len__(self):
		return 0

	def __iter__(self):
		return iter(())

	def __enter__(self):
		return self

	def __exit__(self, exc_class, exc, traceback) -> None:
		pass


class ListStorage(PointsStorage):
	"""Stores points in a list"""

	__slots__ = ("stor", "isSorted")

	def __init__(self) -> None:
		self.stor = []
		self.isSorted = False

	def append(self, params: dict, loss: LossT) -> None:
		self.isSorted = False
		self.stor.append(Point((params, loss)))

	def sort(self) -> None:
		if not (self.isSorted):
			self.stor.sort()
			self.isSorted = True

	def __len__(self):
		return len(self.stor)

	def __iter__(self):
		self.sort()
		for el in self.stor:
			yield Point((dict(el[0]), el[1]))

	def __enter__(self):
		return self

	def __exit__(self, exc_class, exc, traceback) -> None:
		pass


class MemoryStorage(ListStorage):
	"""Stores points in a heap"""

	__slots__ = ()

	def append(self, params: dict, loss: LossT) -> None:
		self.isSorted = False
		heapq.heappush(self.stor, Point((params, loss)))


defaultSQLitePointsCacheFileName = "./UniOptPointsBackup.sqlite"


class SQLiteStorage(PointsStorage):
	"""Stores points in an SQLite DB. Currently uses Cache"""

	__slots__ = ("pointsBackup",)

	def __init__(self, fileName: typing.Union[str, "pathlib.Path"] = defaultSQLitePointsCacheFileName, cacheClass: typing.Type = None) -> None:
		if cacheClass is None:
			cacheClass = JSONCache
		self.pointsBackup = cacheClass(fileName)

	def append(self, params, loss: LossT):
		self.pointsBackup[len(self.pointsBackup)] = (params, loss)

	def __len__(self):
		return len(self.pointsBackup)

	def __iter__(self):
		for hp, loss in self.pointsBackup.values():
			yield Point((hp, loss))

	def __enter__(self):
		self.pointsBackup.__enter__()
		return self

	def __exit__(self, exc_class, exc, traceback) -> None:
		self.pointsBackup.__exit__(exc_class, exc, traceback)
