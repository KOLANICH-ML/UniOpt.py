import warnings

from lazily.poap.controller import BasicWorkerThread, EvalRecord, ThreadController
from lazily.pySOT.experimental_design import SymmetricLatinHypercube
from lazily.pySOT.optimization_problems import OptimizationProblem
from lazily.pySOT.strategy import SRBFStrategy
from lazily.pySOT.surrogate import CubicKernel, LinearTail, RBFInterpolant, SurrogateUnitBox

from UniOpt.core.ProgressReporter import ProgressReporter
from UniOpt.core.Spec import HyperDef

from ..core.ArraySpec import HyperparamArray
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import ArraySpecOnlyBoxes
from ..imports import *


class PySOTSpecObj(HyperparamArray):
	@classmethod
	def dict2native(cls, hyperparamsNative: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		lbs = []
		ubs = []
		typeSelector = {
			int: [],
			float: [],
		}

		for i, (tp, lb, ub) in enumerate(super().dict2native(hyperparamsNative, spec)):
			typeSelector[tp].append(i)
			lbs.append(lb)
			ubs.append(ub)

		res = OptimizationProblem()
		res.dim = len(lbs)
		res.lb = np.array(lbs)
		res.ub = np.array(ubs)
		res.int_var = np.array(typeSelector[int])
		res.cont_var = np.array(typeSelector[float])
		return res


class PySOTSpec(ArraySpecOnlyBoxes):
	hyperparamsSpecType = PySOTSpecObj

	class HyperparamsSpecsConverters:
		def uniform(k, dist, tp):
			return (tp, dist.ppf(0), dist.ppf(1))


class PySOT(GenericOptimizer):
	specType = PySOTSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Dict[str, typing.Union[HyperparamDefinition, int]], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, surrogateClass=None, interpolantClass=None, kernelClass=None, tailClass=None, designClass=None, strategyClass=None) -> None:
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		if surrogateClass is None:
			surrogateClass = SurrogateUnitBox

		if interpolantClass is None:
			interpolantClass = RBFInterpolant
		if kernelClass is None:
			kernelClass = CubicKernel
		if tailClass is None:
			tailClass = LinearTail
		if designClass is None:
			designClass = SymmetricLatinHypercube
		if strategyClass is None:
			strategyClass = SRBFStrategy

		self.surrogateClass = surrogateClass
		self.interpolantClass = interpolantClass
		self.kernelClass = kernelClass
		self.tailClass = tailClass
		self.designClass = designClass
		self.strategyClass = strategyClass

	def injectPoints(self, pointz, bestPointIndex, controller, initialize=False):
		for p in pointz:
			rec = EvalRecord(params=p[0], status="completed")
			rec.value = p[1][0]
			rec.feasible = True
			controller.fevals.append(rec)

	def prepareScoring(self, problem):
		interpolant = self.interpolantClass(dim=problem.dim, kernel=self.kernelClass(), tail=self.tailClass(problem.dim))
		surrogate = self.surrogateClass(interpolant, lb=problem.lb, ub=problem.ub)
		design = self.designClass(dim=problem.dim, num_pts=self.iters)
		controller = ThreadController()
		controller.strategy = self.strategyClass(max_evals=self.iters, asynchronous=True, exp_design=design, surrogate=surrogate, batch_size=self.jobs, opt_prob=problem)
		return (self.iters, "pySOT", controller)

	def invokeScoring(self, fn: typing.Callable, pb: ProgressReporter, controller) -> np.ndarray:
		def pySOTScore(hyperparamsSeq):
			return fn(hyperparamsSeq)[0]

		controller.strategy.opt_prob.eval = pySOTScore

		for _ in range(self.jobs):
			worker = BasicWorkerThread(controller, controller.strategy.opt_prob.eval)
			controller.launch_worker(worker)

		self.details = controller.run()
		res = np.array(self.details.params)
		if len(res.shape) == 2:  # WTF? sometimes it is an array of an array of params in its zeroth element, sometimes it is an array of params itself, depending on if other optimizers have been run before???
			return self.details.params[0]
		else:
			return self.details.params
