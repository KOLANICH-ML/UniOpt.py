from lazily import optunity

from ..core.Optimizer import GenericOptimizer, PointsStorage
from ..core.ProgressReporter import ProgressReporter
from ..core.Spec import *
from ..core.SpecOnlyBoxes import *
from ..imports import *


class OptunityOptimizer(GenericOptimizer):
	specType = SpecOnlyBoxesNoIntegers

	solver = None

	def prepareScoring(self, spaceSpec):
		optunityParams = optunity.suggest_solver(self.iters, self.__class__.solver, **spaceSpec)  # it's not only suggests, it initializes the params to pass to solver
		return (self.iters, "optunity " + optunityParams["solver_name"], {"optunityParams": optunityParams, "spaceSpec": spaceSpec})

	def invokeScoring(self, fn, pb, ctx):
		def optunityScore(**hyperparams):
			res = fn(hyperparams)
			# return (-res[0], -res[1])
			return -res[0]

		optunityScore_ = optunity.wrap_constraints(optunityScore, sys.float_info.max, range_oc=ctx["spaceSpec"])  # FUCK, it just skips these iterations
		# optunityScore_=optunity.wrap_constraints(optunityScore, range_oc=ctx["spaceSpec"])

		solver = optunity.make_solver(**ctx["optunityParams"])

		(best, self.details) = optunity.optimize(solver=solver, func=optunityScore_, maximize=False, max_evals=self.iters)
		# details.optimum
		# details.call_log - dict (keys are arguments names) of lists each one value corresponds to an arg of each call
		# details.report
		# details.time
		return best


class NelderMead(OptunityOptimizer):
	solver = "nelder-mead"


class Sobol(OptunityOptimizer):
	solver = "sobol"


class ParticleSwarm(OptunityOptimizer):
	solver = "particle swarm"


class CMA_ES(OptunityOptimizer):
	solver = "cma-es"


class RandomSearch(OptunityOptimizer):
	solver = "random search"


class GrigSearch(OptunityOptimizer):
	solver = "grid search"
