import warnings

from lazily import de, ypstruct

from UniOpt.core.ProgressReporter import ProgressReporter
from UniOpt.core.Spec import HyperDef

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import ArraySpecOnlyBoxesNoIntegers
from ..imports import *


class YPDESpec(ArraySpecOnlyBoxesNoIntegers):
	class HyperparamsSpecsConverters:
		def uniform(k, dist, tp):
			return dist

	def distributionToUniform(self, k: str, hpDef: HyperDef) -> HyperDef:
		return self.distributionToUniform_(k, hpDef)


class YPDE(GenericOptimizer):
	specType = YPDESpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Dict[str, typing.Union[HyperparamDefinition, int]], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, popSize: int = 30, mutation: float = 0.8, crossover: float = 0.7) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)

		restIters = self.iters - popSize
		self.generations = restIters / popSize
		assert (self.generations).is_integer()
		self.generations = int(self.generations)
		assert self.generations > 0

		self.popSize = popSize
		self.crossover = crossover
		self.mutation = mutation

	def prepareScoring(self, specSeq: typing.Iterable[scipy.stats._distn_infrastructure.rv_frozen]) -> typing.Tuple[int, str, typing.Tuple["ypstruct.structure", "ypstruct.structure"]]:
		problem = ypstruct.structure()
		problem.varmin = uniformLimits[0]
		problem.varmax = uniformLimits[1]
		problem.nvar = len(specSeq)

		params = ypstruct.structure()
		params.maxit = self.generations
		params.npop = self.popSize
		params.F = self.mutation
		params.CR = self.crossover
		params.DisplayInfo = False
		return (self.iters, "ypde", (problem, params))

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, context: typing.Tuple["ypstruct.structure", "ypstruct.structure"]) -> np.ndarray:
		def ypdeScore(hyperparamsSeq):
			return fn(hyperparamsSeq)[0]

		(problem, params) = context
		problem.objfunc = ypdeScore

		res = de.run(problem, params)
		self.detail = res
		return res.bestsol.position
