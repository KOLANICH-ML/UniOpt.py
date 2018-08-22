from ..imports import *
from .HyperparamVector import HyperparamVector
from .Optimizer import GenericOptimizer
from .Spec import Spec


class HyperparamArray(HyperparamVector):
	primitiveType = list

	@classmethod
	def dict2native(cls, dic: typing.Dict[str, typing.Any], spec) -> typing.Iterable[typing.Any]:
		if dic:
			res = [None] * len(spec.spec.keys())
			#res = [None] * len(spec.indexes.keys())
			for k, v in dic.items():
				res[spec.indexes[k]] = v
			return res
		else:
			return None

	@staticmethod
	def native2dict(native: typing.Iterable[typing.Any], spec) -> typing.Dict[str, typing.Any]:
		"""Transforms a object of native output type into a dict of a spec"""
		if native is not None:
			keys = list(spec.spec.keys())
			return {spec.rIndexes[i]: v for i, v in enumerate(native)}
		else:
			return None


class ArraySpec(Spec):
	"""Optimizer receives arrays as a spec"""

	hyperparamsVectorType = HyperparamArray
	hyperparamsSpecType = HyperparamArray

	def __init__(self, spec):
		super().__init__(spec)
		self.indexes = {k: i for i, k in enumerate(self.spec)}
		self.rIndexes = tuple(self.spec.keys())
		self.maxIndex = len(self.indexes)
