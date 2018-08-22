import typing
import warnings
from functools import partial

import numpy as np
from lazily import hyperengine
from lazy_object_proxy import Proxy
from numpy import float64

from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..imports import *
from ..utils import dummyFunction


class BlackBoxSolver:
	def __init__(self, func):
		self.func = func
		self._val_loss_curve = []

	def train(self):
		loss = self.func()
		self._val_loss_curve.append(loss)
		return self._reducer(self._val_loss_curve)

	def _reducer(self, *args, **kwargs):
		return min(*args, **kwargs)

	def terminate(self):
		pass


class HyperEngineSpec(MSpec(scalarMode=ScalarMetaMap.degenerateCategory, integerMode=IntegerMetaMap.noIntegers)):
	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return __class__._categorical(k, range(int(dist.a), int(dist.b)))

		def uniform(k, dist, tp):
			return hyperengine.spec.uniform(dist.ppf(0), dist.ppf(1))

		# normal and etc are implemented through a ppf, no sense to make intrinsic support
		def _categorical(k, categories):
			return hyperengine.spec.choice(categories)


class HyperEngine(GenericOptimizer):
	specType = HyperEngineSpec
	hyperTunerStrategy = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, **strategy_params) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		self.strategy_params = strategy_params
		if hyperengine.base.logging.log is not dummyFunction:
			hyperengine.base.logging.log = dummyFunction

	def injectPoints(self, pointz, bestPointIndex, tuner, initialize=False):
		for numInjectedPoints, p in enumerate(pointz):
			x = p[0]
			x1 = np.zeros(len(tuner._parsed._spec))
			for i, k in enumerate(tuner._parsed._spec):
				x1[i] = x[k]
			tuner._strategy.add_point(x1, p[1][0])
		tuner._max_points += numInjectedPoints

	def prepareScoring(self, specDict: typing.Dict[str, typing.Union["hyperengine.spec.nodes.UniformNode", int]]) -> typing.Tuple[int, str, "hyperengine.HyperTuner"]:
		tuner = hyperengine.HyperTuner(specDict, solver_generator=None, max_points=self.iters, strategy=self.__class__.hyperTunerStrategy, **self.strategy_params)
		return (self.iters, "HyperTuner " + self.__class__.hyperTunerStrategy, tuner)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, tuner) -> typing.Dict[str, NumericT]:
		def htScore(hyperparamsDict):
			return fn(hyperparamsDict)[0]

		def solverGenerator(hyperparams):
			return BlackBoxSolver(partial(htScore, hyperparams))

		tuner._solver_generator = solverGenerator
		tuner.tune()
		return tuner._parsed.instantiate(tuner._strategy.points[np.argmin(tuner._strategy.values)])


class HyperEngineBayesian(HyperEngine):
	hyperTunerStrategy = "bayesian"


def createDefaultPortfolioMethods():
	from hyperengine.bayesian.strategy import utilities

	return tuple(utilities.keys())


defaultPortfolioMethods = Proxy(createDefaultPortfolioMethods)


class HyperEnginePortfolio(HyperEngine):
	hyperTunerStrategy = "portfolio"

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, **strategy_params):
		if "methods" not in strategy_params:
			strategy_params["methods"] = defaultPortfolioMethods
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, **strategy_params)
