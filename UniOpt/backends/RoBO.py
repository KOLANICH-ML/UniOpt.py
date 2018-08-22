import warnings

from lazily.robo.fmin import bayesian_optimization

from UniOpt.core.ProgressReporter import ProgressReporter
from UniOpt.core.Spec import HyperDef

from ..core.ArraySpec import HyperparamArray
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import ArraySpecOnlyBoxesNoIntegers
from ..imports import *


class RoBOSpecArrayDict(HyperparamArray):
	@classmethod
	def dict2native(cls, hyperparamsNative: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		spaceSpec = np.array(super().dict2native(hyperparamsNative, spec))
		return {"lower": spaceSpec[:, 0], "upper": spaceSpec[:, 1]}


class RoBOSpec(ArraySpecOnlyBoxesNoIntegers):
	hyperparamsSpecType = RoBOSpecArrayDict

	class HyperparamsSpecsConverters:
		def uniform(k, dist, tp):
			return (dist.ppf(0), dist.ppf(1))


class RoBO(GenericOptimizer):
	specType = RoBOSpec
	modelType = None

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Dict[str, typing.Union[HyperparamDefinition, int]], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, acquisitionOptimizerType="random", acquisitionType="log_ei") -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		self.acquisitionType = acquisitionType.lower()
		self.acquisitionOptimizerType = acquisitionOptimizerType

	def prepareScoring(self, specArrayDict):
		context = type(specArrayDict)(specArrayDict)
		context["X_init"] = np.array([])
		context["Y_init"] = np.array([])
		return (self.iters, "RoBO (" + self.__class__.modelType + ")", specArrayDict)

	def injectPoints(self, pointz, bestPointIndex, context, initialize=False):
		points = []
		losses = []
		for p in pointz:
			points.append(p[0])
			losses.append(p[1][0])
		points = np.array(points)
		losses = np.array(losses)

		if initialize:
			context["X_init"] = points
			context["Y_init"] = losses
		else:
			context["X_init"] = np.concatenate(points, context["X_init"])
			context["Y_init"] = np.concatenate(losses, context["Y_init"])

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, context) -> np.ndarray:
		def roboScore(hyperparamsSeq):
			return fn(hyperparamsSeq)[0]

		self.details = bayesian_optimization(roboScore, num_iterations=self.iters, maximizer=self.acquisitionOptimizerType, acquisition_func=self.acquisitionType, model_type=self.__class__.modelType, n_init=3, **context)
		return self.details["x_opt"]


class RoBOGPMCMC(RoBO):
	modelType = "gp_mcmc"


class RoBOGP(RoBO):
	modelType = "gp"


class RoBOForest(RoBO):
	modelType = "rf"


class RoBOBohamiann(RoBO):
	modelType = "bohamiann"
