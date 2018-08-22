import typing

from lazily import skopt
from lazy_object_proxy import Proxy

from ..core.MetaSpec import *
from ..core.Optimizer import *
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..imports import *


def getTypeRemap():
	return {int: skopt.space.Integer, float: skopt.space.Real}


typeRemap = Proxy(getTypeRemap)


class SKOptSpec(MSpec(isArray=True, scalarMode=ScalarMetaMap.degenerateCategory)):
	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return __class__._categorical(k, range(dist.a, dist.b))

		def uniform(k, dist, tp):
			return typeRemap[tp](dist.ppf(0), dist.ppf(1), name=k)

		def _categorical(k, categories):
			return skopt.space.Categorical(categories, name=k)


class SKOpt(GenericOptimizer):
	specType = SKOptSpec
	skoptAlgo = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, acquisitionOptimizerType="auto", acquisitionType="gp_hedge", chi: float = 0.01, kappa: float = 1.96, nInitialPoints: int = 10, nRestartsOptimizer: int = 5):
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		self.acquisitionType = acquisitionType
		self.acquisitionOptimizerType = acquisitionOptimizerType

		self.chi = chi
		self.kappa = kappa
		self.nInitialPoints = nInitialPoints
		self.nRestartsOptimizer = nRestartsOptimizer

	def prepareScoring(self, spaceSpec: typing.Tuple["skopt.space.space.Real", "skopt.space.space.Integer", "skopt.space.space.Categorical"]) -> typing.Tuple[int, str, typing.Tuple["skopt.space.space.Real", "skopt.space.space.Integer", "skopt.space.space.Categorical"]]:
		from skopt.utils import cook_estimator, normalize_dimensions

		normalized = normalize_dimensions(spaceSpec)
		base_estimator = cook_estimator(self.__class__.skoptAlgo, space=normalized, random_state=None)
		optimizer = skopt.Optimizer(normalized, base_estimator, n_initial_points=0, acq_func=self.acquisitionType, acq_optimizer=self.acquisitionOptimizerType, acq_optimizer_kwargs={"n_points": self.iters, "n_restarts_optimizer": self.nRestartsOptimizer, "n_jobs": self.jobs}, acq_func_kwargs={"xi": self.chi, "kappa": self.kappa})
		return (self.iters, "SKOpt (" + self.__class__.skoptAlgo + ")", optimizer)

	def injectPoints(self, pointz, bestPointIndex, optimizer, initialize=False):
		for p in pointz:
			optimizer.tell(p[0], p[1][0])
			self.nInitialPoints -= 1
		if self.nInitialPoints < 0:
			self.nInitialPoints = 0

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, optimizer) -> typing.List[NumericT]:
		optimizer._n_initial_points = self.nInitialPoints
		for i in range(self.iters):
			hp = optimizer.ask()
			loss = fn(hp)
			result = optimizer.tell(hp, loss[0])
		self.details = result
		return result.x


class SKOptBayesian(SKOpt):
	skoptAlgo = "GP"


class SKOptExtraTrees(SKOpt):
	skoptAlgo = "ET"


class SKOptForest(SKOpt):
	skoptAlgo = "RF"


class SKOptGBTree(SKOpt):
	skoptAlgo = "GBRT"


class SKOptRandom(SKOpt):
	skoptAlgo = "dummy"
