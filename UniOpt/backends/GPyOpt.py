from lazily import GPyOpt

from ..core.MetaSpec import *
from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..imports import *
from ..utils import notInitializedFunction


class GPyOptSpec(MSpec(isArray=True, scalarMode=ScalarMetaMap.degenerateCategory, integerMode=IntegerMetaMap.floatIntegers)):
	class HyperparamsSpecsConverters:
		def randint(k, dist, tp):
			return __class__._categorical(k, range(dist.a, dist.b))

		def uniform(k: str, dist, tp: type):
			if tp is float:
				return {"name": k, "domain": (dist.ppf(0), dist.ppf(1)), "type": "continuous"}
			else:
				return __class__._categorical(k, range( int(dist.ppf(0)), int(dist.ppf(1)) ))
				# {'name': k, 'domain': range(int(dist.ppf(0)), int(dist.ppf(1))), "type": "discrete"}

		def _categorical(k, categories):
			return {"name": k, "domain": categories, "type": "discrete"}  # in gpyopt categorical returns one-hot


class GPyOptOptimizer(GenericOptimizer):
	specType = GPyOptSpec

	def __init__(self, blackBoxFunc: typing.Callable, spaceSpec: typing.Mapping[str, object], iters: int = 1000, jobs: int = 3, pointsStorage: PointsStorage = None, acquisitionOptimizerType="lbfgs", acquisitionType="EI", acquisitionTradeoff: float = 0.1, modelType="GP", initialDesignNumData=5, initialDesignType="random", exactFeval=False, modelUpdateInterval=1, evaluatorType="sequential", batchSize=1, dedup=False, eps=0, modular=False):
		super().__init__(blackBoxFunc, spaceSpec, iters, jobs, pointsStorage)
		self.modelType = modelType
		self.acquisitionType = acquisitionType
		self.batchSize = batchSize
		self.eps = eps
		self.evaluatorType = evaluatorType
		self.acquisitionTradeoff = acquisitionTradeoff
		self.exactFeval = exactFeval
		self.acquisitionOptimizerType = acquisitionOptimizerType
		self.modelUpdateInterval = modelUpdateInterval
		self.initialDesignType = initialDesignType
		self.initialDesignNumData = initialDesignNumData
		self.modular = modular

	def prepareScoring(self, specSeq):
		optimizer = GPyOpt.methods.BayesianOptimization(f=None, domain=specSeq, model_type=self.modelType, acquisition_type=self.acquisitionType, evaluator_type=self.evaluatorType, maximize=False, verbosity=True, verbosity_model=True, de_duplication=True, num_cores=self.jobs, batch_size=self.batchSize, eps=self.eps, initial_design_type=self.initialDesignType, initial_design_numdata=self.initialDesignNumData, exact_feval=self.exactFeval, acquisition_optimizer_type=self.acquisitionOptimizerType, model_update_interval=self.modelUpdateInterval, X=np.empty((0, len(specSeq))), Y=np.empty((0, 1)), acquisition_weight=self.acquisitionTradeoff)  # vital to make it do all the iterations
		optimizer.X = None
		optimizer.Y = None
		optimizer.modular_optimization = self.modular
		return (self.iters, "GPyOpt", optimizer)

	def injectPoints(self, pointz, bestPointIndex, optimizer, initialize=False):
		hps = []
		losses = []
		for p in pointz:
			hps.append(p[0])
			losses.append([p[1][0]])
		hps = np.array(hps)
		losses = np.array(losses)
		print(hps)
		if optimizer.X is None:
			optimizer.X = np.empty((0, len(hps[0])))
			optimizer.Y = np.empty((0, 1))

		optimizer.X = np.concatenate((optimizer.X, hps), axis=0)
		optimizer.Y = np.concatenate((optimizer.Y, losses), axis=0)
		#optimizer.cost.update_cost_model(hps, times)?

	def invokeScoring(self, fn, pb, optimizer):
		def gpyScore(hyperparams):
			res = fn(hyperparams[0])
			return res[0]

		optimizer.f = optimizer._sign(gpyScore)

		optimizer.objective = GPyOpt.core.task.objective.SingleObjective(optimizer.f, optimizer.batch_size, optimizer.objective_name)
		optimizer._init_design_chooser()

		optimizer.run_optimization(max_iter=self.iters - self.initialDesignNumData)
		self.details = optimizer
		best = optimizer.X[np.argmin(optimizer.Y)]
		return best
