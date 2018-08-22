from ..imports import *
from .HyperparamVector import HyperparamVector
from .MetaMap import MetaMap
from .Optimizer import GenericOptimizer
from .Spec import HyperparamDefinition, Spec
from .SpecNoIntegers import *


class SpecNoScalars(Spec):
	"""A spec not supporting scalars"""

	pass


def returnNone(x):
	pass


class SpecNoScalarsDumb(SpecNoScalars):
	"""Saves scalars itself, then augment the result"""

	hyperparamsVectorType = HyperparamVector

	def __init__(self, genericSpec):
		self.savedScalarHyperparamsNames = []
		super().__init__(genericSpec)

	def scalarProcessor(self, i, k, v):
		#v = super().scalarProcessor(i, k, v) # assuming that a user has provided the scalar in right format, no postprocessing needed at all

		def returnV(arg):
			return v

		self.savedScalarHyperparamsNames.append(k)
		self.postProcessors[k].insert(0, (returnV, returnNone))
		# return res


class SpecNoScalarsCategorical(SpecNoScalars):
	"""Creates a degenerate category"""

	def scalarProcessor(self, i, k, v):
		return super().scalarProcessor(i, k, (v,))


class ScalarMetaMap(MetaMap):
	supportsScalars = None
	degenerateCategory = ("Categorical", SpecNoScalarsCategorical)
	noScalars = ("Dumb", SpecNoScalarsDumb)
