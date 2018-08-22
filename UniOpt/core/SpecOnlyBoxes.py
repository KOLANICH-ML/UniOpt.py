from ..core.MetaSpec import *
from ..imports import *
from .HyperparamVector import HyperparamVector
from .Spec import HyperparamDefinition, Spec


class SpecOnlyBoxes(MSpec(scalarMode=ScalarMetaMap.noScalars)):
	"""A very dumb spec, allowing only uniformly distributed variables, no categoricals and scalars and internal space spec is just a sequence `(lower_bound, upper_bound)`. A widespread situation."""

	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return (dist.a, dist.b)

		def uniform(k, dist, tp):
			return (dist.ppf(0), dist.ppf(1))


class SpecOnlyBoxesNoIntegers(MSpec(integerMode=IntegerMetaMap.noIntegers), SpecOnlyBoxes):
	pass


class ArraySpecOnlyBoxes(MSpec(isArray=True, scalarMode=ScalarMetaMap.noScalars), SpecOnlyBoxes):
	pass


class ArraySpecOnlyBoxesNoIntegers(MSpec(isArray=True, scalarMode=ScalarMetaMap.noScalars, integerMode=IntegerMetaMap.noIntegers), SpecOnlyBoxes):
	pass
