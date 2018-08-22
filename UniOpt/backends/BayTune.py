import typing
from functools import partial

from lazily import hyperopt
from lazily.btb.hyper_parameter import CatHyperParameter, FloatHyperParameter, HyperParameter, IntHyperParameter, ParamTypes
from lazily.btb.tuning import GCP, GP, GCPEi, GCPEiVelocity, GPEi, GPEiVelocity
from lazy_object_proxy import Proxy

from ..core.HyperparamVector import HyperparamVector
from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.Spec import HyperparamDefinition
from ..imports import *


class BayTuneSpec(MSpec(scalarMode=ScalarMetaMap.degenerateCategory)):
	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return IntHyperParameter(ParamTypes.INT, dist.a, dist.b)

		def uniform(k, dist, tp):
			if tp is int:
				tpE = ParamTypes.INT
			elif tp is float:
				tpE = ParamTypes.FLOAT
			else:
				raise NotImplementedError(tp)
			return HyperParameter(tpE, [dist.ppf(0), dist.ppf(1)])  # do not call specialized classes, there is a bug causing __new__ return None in the base class in tuese cases

		#def norm(k, dist, tp):
		#	ctor=(NormalIntegerHyperparameter if tp is int else NormalFloatHyperparameter)
		#	return ctor(k, dist.mean(), dist.std(), default_value=tp(dist.mean()))
		def _categorical(k, categories):
			return CatHyperParameter(ParamTypes.INT_CAT, categories)


class BayTune(GenericOptimizer):
	specType = BayTuneSpec
	tunerClass = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

	def prepareScoring(self, spaceSpec):
		spaceSpec = list(spaceSpec.items())
		tuner = self.__class__.tunerClass(spaceSpec)
		return (self.iters, "BayTune", tuner)

	def injectPoints(self, pointz, bestPointIndex, tuner, initialize=False):
		for p in pointz:
			tuner.add(p[0], p[1][0])

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, tuner) -> typing.Dict[str, typing.Union[float, int]]:
		for i in range(self.iters):
			hp = tuner.propose()
			loss = -fn(hp)[0]
			tuner.add(hp, loss)
		self.details = tuner
		return tuner._best_hyperparams


class BayTuneGP(BayTune):
	tunerClass = GP


class BayTuneGPEi(BayTuneGP):
	tunerClass = GPEi


class BayTuneGPEiVelocity(BayTuneGPEi):
	tunerClass = GPEiVelocity


class BayTuneGCP(BayTune):
	tunerClass = GCP


class BayTuneGCPEi(BayTuneGCP):
	tunerClass = GCPEi


class BayTuneGCPEiVelocity(BayTuneGCPEi):
	tunerClass = GCPEiVelocity
