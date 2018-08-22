from ..imports import *
from .HyperparamVector import HyperparamVector
from .MetaMap import MetaMap
from .Optimizer import GenericOptimizer
from .Spec import DummySpec, HyperDef, HyperparamDefinition, Spec, SpecMeta, categoricalTypes, float2int


class SpecToIntegersMeta(SpecMeta):
	"""A metaclass to process integerCtor ."""

	integerCtors = set()

	def __new__(cls, className, parents, attrs, *args, **kwargs):
		if "integerCtor" in attrs:
			__class__.integerCtors.add(attrs["integerCtor"])
		return super().__new__(cls, className, parents, attrs, *args, **kwargs)


class SpecToIntegersBase(Spec, metaclass=SpecToIntegersMeta):
	"""Transforms floats into integers."""

	def integerCtor(val: float):
		raise NotImplementedError()

	def scalarProcessor(self, i, k, v):
		res = super().scalarProcessor(i, k, v)
		return res

	def addAnIntegerCheckPostprocessorIfNeeded(self, i, k, v):
		pp = self.postProcessors[k]
		if not pp or pp[-1] not in __class__.__class__.integerCtors:
			pp.append((self.__class__.integerCtor, float))

	def addAPostProcessorIfNeeded(self, i, k, v):
		if isinstance(v, HyperDef) and issubclass(v.type, int) or isinstance(v, categoricalTypes) and isinstance(v[0], int) or isinstance(v, int):
			self.addAnIntegerCheckPostprocessorIfNeeded(i, k, v)


class SpecToIntegers(SpecToIntegersBase):
	integerCtor = int


class SpecNoIntegers(SpecToIntegersBase):
	integerCtor = float2int


class IntegerMetaMap(MetaMap):
	supportsIntegers = None
	floatIntegers = ("To", SpecToIntegers)
	noIntegers = ("No", SpecNoIntegers)
