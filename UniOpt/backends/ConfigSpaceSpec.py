from lazily.ConfigSpace import ConfigurationSpace
from lazily.ConfigSpace.hyperparameters import CategoricalHyperparameter, Constant, NormalFloatHyperparameter, NormalIntegerHyperparameter, UniformFloatHyperparameter, UniformIntegerHyperparameter

from ..core.HyperparamVector import HyperparamVector
from ..core.MetaSpec import *
from ..imports import *


class ConfigSpaceSpecVec(HyperparamVector):
	@classmethod
	def dict2native(cls, dic: typing.Dict[str, typing.Any], spec) -> typing.Iterable[typing.Any]:
		if dic:
			cs = ConfigurationSpace()
			print(dic, list(dic.values()))
			cs.add_hyperparameters(dic.values())
			return cs
		else:
			return None


class ConfigSpaceSpec(MSpec()):
	hyperparamsVectorType = HyperparamVector
	#hyperparamsVectorType = HyperparamArray
	hyperparamsSpecType = ConfigSpaceSpecVec

	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return UniformIntegerHyperparameter(k, dist.a, dist.b)

		def uniform(k, dist, tp):
			ctor = UniformIntegerHyperparameter if tp is int else UniformFloatHyperparameter
			return ctor(name=k, lower=dist.ppf(0), upper=dist.ppf(1))

		#def norm(k, dist, tp):
		#	ctor=(NormalIntegerHyperparameter if tp is int else NormalFloatHyperparameter)
		#	return ctor(k, dist.mean(), dist.std(), default_value=tp(dist.mean()))
		def _categorical(k, categories):
			return CategoricalHyperparameter(k, categories)

	def scalarProcessor(self, i, k, v):
		return Constant(k, v)
