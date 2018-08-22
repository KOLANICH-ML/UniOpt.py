import typing

from lazily import pyshac
from lazy_object_proxy import Proxy

from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.SpecOnlyBoxes import HyperparamVector
from ..imports import *


def loadPyShacGridSpec():
	from pyshac import DiscreteHyperParameter, NormalContinuousHyperParameter, UniformContinuousHyperParameter
	from pyshac.config.hyperparameters import AbstractContinuousHyperParameter

	class SciPyContinuousHyperParameter(AbstractContinuousHyperParameter):
		def __init__(self, k, dist):
			self.dist = dist
			super().__init__(k, dist.a, dist.b, False)

		def sample(self):
			return dist.rvs(1)[0]

		def get_config(self):
			config = super().get_config()
			config.update({"dist": self.dist})
			return config

	class PySHACGridSpec(MSpec(isArray=True, scalarMode=ScalarMetaMap.degenerateCategory, integerMode=IntegerMetaMap.noIntegers)):
		hyperparamsVectorType = HyperparamVector

		class HyperparamsSpecsConverters:
			def randint(k, dist, tp):
				return __class__._categorical(k, range(dist.a, dist.b))

			def uniform(k, dist, tp):
				return UniformContinuousHyperParameter(k, dist.ppf(0), dist.ppf(1))

			def norm(k, dist, tp):
				return NormalContinuousHyperParameter(k, dist.mean(), dist.std())

			def _categorical(k, categories):
				return DiscreteHyperParameter(k, categories)

		def transformHyperDefItemUniversal(self, k, v):
			return SciPyContinuousHyperParameter(k, v.distribution)

		def transformResult(self, hyperparamsNative):
			return super().transformResult(self.__class__.hyperparamsSpecType.native2dict(hyperparamsNative, self))

	return PySHACGridSpec


PySHACGridSpec = Proxy(loadPyShacGridSpec)


class PySHAC(GenericOptimizer):
	specType = PySHACGridSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, batches=None, skipCV: bool = False, earlyStop: bool = False, relaxChecks: bool = False, engine=None, **otherShacHyperparams) -> None:
		ratio = 10
		if batches is None:
			batches = round(iters / ratio)
			warnings.warn("Count of batches is not set, assumming iters/" + str(ratio))
		if not batches:
			batches = 1
			warnings.warn("Count of batches 0, setting to " + str(batches))

		ratio = round(iters / batches)
		iters1 = batches * ratio
		if iters1 != iters:
			warnings.warn("Count of iters is not divided by count of batches. Rounding to" + str(iters1))
		iters = iters1

		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

		if engine is None:
			engine = pyshac.SHAC

		self.engine = engine
		self.batches = batches
		self.skipCV = skipCV
		self.earlyStop = earlyStop
		self.relaxChecks = relaxChecks
		self.otherShacHyperparams = otherShacHyperparams

	def prepareScoring(self, spaceSpec: typing.Iterable["pyshac.config.hyperparameters.AbstractHyperParameter"]) -> typing.Tuple[int, str, "pyshac.SHAC"]:
		shacHyperparams = {"total_budget": self.iters, "num_batches": self.batches, "objective": "min"}
		shacHyperparams.update(self.otherShacHyperparams)

		shac = self.engine(spaceSpec, **shacHyperparams)
		shac.num_parallel_generators = self.jobs
		shac.num_parallel_evaluators = self.jobs
		# shac.generator_backend = 'multiprocessing'
		# shac.generator_backend = 'threading'

		warnings.warn("Problem passing data between processes, https://github.com/titu1994/pyshac/issues/1 , setting evaluator_backend = 'threading'")
		# shac.num_parallel_evaluators = 1
		shac.evaluator_backend = "threading"
		# shac.evaluator_backend = 'multiprocessing'

		return (self.iters, "pyshac", shac)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, shac: "pyshac.SHAC") -> typing.List[float]:
		def pyshacScore(id, hyperparamsDict):
			return fn(hyperparamsDict)[0]

		shac.fit(pyshacScore, skip_cv_checks=self.skipCV, early_stop=self.earlyStop, relax_checks=self.relaxChecks)
		return shac.dataset.X[np.argmin(shac.dataset.Y)]
