from ..imports import *
from .HyperparamVector import HyperparamVector
from .MetaMap import MetaMap
from .Optimizer import GenericOptimizer
from .Spec import HyperparamDefinition, Spec
from .SpecNoIntegers import *


class SpecNoCategories(Spec):
	"""A mixing implementing optimization of categorical variables with optimizers which don't support them, but support numbers"""

	hyperparamsVectorType = HyperparamVector

	def __init__(self, genericSpec):
		raise NotImplementedError()
		super().__init__(genericSpec)

	def scalarProcessor(self, i, k, v):
		raise NotImplementedError()
		v = super().scalarProcessor(i, k, v)

		def returnV(arg):
			raise NotImplementedError()

		self.postProcessors[k].insert(0, (returnV, None))


class CategoriesMetaMap(MetaMap):
	supportsCategories = None
	noCategories = None


raise NotImplementedError()
