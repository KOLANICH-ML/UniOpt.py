__all__ = ("SKLearnRigidGridSpec", "SKLearnRandomizedSpec")
import typing

import scipy.stats

from ..core.MetaSpec import *
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.Spec import HyperparamDefinition
from ..imports import *

msel = lazyImport("sklearn.model_selection")

# msel.GridSearchCV
# msel.RandomizedSearchCV


class SKLearnSpec(MSpec(scalarMode=ScalarMetaMap.degenerateCategory, integerMode=IntegerMetaMap.noIntegers)):
	pass


class SKLearnRigidGridSpec(SKLearnSpec):
	class HyperparamsSpecsConverters:
		def randint(k, dist):
			return range(v.lower, v.upper, 1)

		def uniform(k, dist):
			return np.linspace(dist.ppf(0), dist.ppf(1), count)


class SKLearnRandomizedSpec(SKLearnSpec):
	def transformHyperDefItemUniversal(self, k: str, v: typing.Union[typing.Tuple[int], HyperparamDefinition]) -> typing.Union[typing.Tuple[int], scipy.stats._distn_infrastructure.rv_frozen]:
		if isinstance(v, categoricalTypes):
			return v
		return v.distribution
