from lazily import bayes_opt

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.SpecOnlyBoxes import *
from ..imports import *


class Bayesian(GenericOptimizer):
	specType = SpecOnlyBoxesNoIntegers

	def __init__(self, blackBoxFunc, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, initPoints=None):
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		if initPoints is None:
			initPoints = iters // 10
		if not initPoints:
			initPoints = 1
		self.initPoints = initPoints

	def injectPoints(self, pointz, bestPointIndex, optimizer, initialize=False):
		for p in pointz:
			optimizer.register(params=p[0], target=-p[1][0])

	def prepareScoring(self, spaceSpec):
		optimizer = bayes_opt.BayesianOptimization(None, spaceSpec, verbose=0)
		return (self.iters, "bayesian", optimizer)

	def invokeScoring(self, fn, pb, optimizer):
		def boScore(**hyperparams):
			res = fn(hyperparams)
			return -res[0]

		optimizer._space.target_func = boScore
		optimizer.maximize(init_points=self.initPoints, n_iter=self.iters - self.initPoints)

		max = optimizer.max
		bestScore = -max["target"]
		best = max["params"]
		self.details = optimizer._space
		return best
