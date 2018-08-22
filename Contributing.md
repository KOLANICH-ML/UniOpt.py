Contributing guidelines
=======================

This project has a bit different policy than the rest of other projects have. Please read it carefully, otherwise it would be very surprising.

Style guide
-----------
0. We don't follow PEP-8.
1. Tabs and spaces are controlled by `.editorconfig` file. See https://editorconfig.org/ for more info about its format. [Install a plugin](https://editorconfig.org/#download) for your IDE/text editor if it doesn't support it out of the box.
2. No manual line wrapping. Wrapping is done by text editor. Enable this feature.

And some very opinionated things
--------------------------------
1. The joke about dead python is not going to be removed. It's the message that everyone should drop python 2 as soon as possible. If you find it inappropriate it's your own personal problem.
2. We really DON'T support python 2, so don't send PRs fixing py2 support. I'm sorry, but this coup de grace is a necessity. With python 4 not so far we don't want to support a serpentarium of different python versions. Since python 3 works fine on a very ancient 1999 year hardware and 2001 year old OS there shouldn't be a serious reason to stay on py 2. If your org cannot or is afraid to migrate to later versions of python, it's your and your org problem, not ours. I advise you to start migrating as soon as possible, to make yourself ready for the moment py2 officially dropped by PSF, you have to migrate anyway sooner or later, if you are not dropping python at all. You can use the fact that many projects are dropping python 2 support to persuade your boss that you have to migrate. Fix your tests if you don't trust them, use 2to3, fix after it, make the code to pass the tests. You also may expect python 3 support being dropped not so far after python 4 release (it depends on if it requires to replace the hardware and the OS, for example pythons >3.5 have no support for Windows XP, and XP is needed for old (but good) hardware costing several millions of $ and having no drivers for Windows 7 or Linux).

And now when the brief organizational FAQ is over, the docs about the architecture.

Architecture guide
==================

As already mentioned, it is easy to add an own backend. Here is an approximate algorithm.

0. Read his guide entirely and get yourself familiar to the conventions used in this library.
	* `HyperparamVector` is a class encapsulating the most generic aspects of a hyperparam vector. Shouldn't be instantiated.
		* `dict2native` transforming a dict into an object of native output type of a spec.
		* `native2dict` transforming an object of native output type into a dict of a spec.
	* `Spec` is a class storing and transforming generic search space specification into an optimizer-specific one. It must have some properties:
		* `hyperparamsVectorType:HyperparamVector` is a type of a vector.
		* `hyperparamsSpecType:HyperparamVector` is a type of a spec itself.
	* `Spec`s are built via mixins. Because it is tricky to remember the right order of inheritance, and because we don't want to precreate them all (exponentially many from the count of mixins) `MSpec` is the function creating the spec class for you. See the detailed description later.
		* `name` - a desired name, don't use: the names are generated automatically
		* `isDummy` - do not transform spec items. Used for testing.
	* `Optimizer` is a class doing optimization. It may get additional arguments. It must have some properties/methods:
		* `specType` - Is a type of a spec.
		* `prepareScoring` - a method setting up scoring. It is your chance to do something before progressbar appeared. It checks correctness, creates objects and returns a `tuple` of
			0. count of function evaluations. You usually need `self.iters` here.
			1. name of optimizer to display on the progressbar.
			2. a context object. You should put there a maximally prepared evaluator.
		* `invokeScoring` - receives a black-box function to optimize, a progressbar object and the context created by `prepareScoring`. This function is called in the context of progressbar. Progressbar object can be used to send messages to progressbar. Usually you wrap the black box function into own one, transforming its results to the format convenient to the optimizer.
	* `ProgressReporter` is a class to report progress. Just install `tqdm` and it would pick that up.
	* All the dependencies are imported with `lazyImport`. Imported package shouldn't be accessed in the main scope because this will cause actual import which will cause lags or errors, if the dependency is not available. If you need to do some preparative work, use `lazy_object_proxy.Proxy` for it.
1. Find an example for the backend. Play with it a little. Determine the following:
	* the format of a space spec:
		* if it allows integers. This influences `integerMode:IntegerMetaMap` argument of `MSpec`:
			* `supportsIntegers` - the optimizer supports specifying integers  and returns them as `int`. No action needed.
			* `floatIntegers` - the optimizer supports integers, but returns them as `float`
			* `noIntegers` - the optimizer doesn't support integers. We have to postprocess with rounding which drastically impacts performance.
		* if it allows plugging variables not from uniform distribution. If it does, you need to define `HyperparamsSpecsConverters` in your class, or use `transformHyperDefItemUniversal`.
		* if it is very dumb, allows only uniform distribution, disallows categories and scalars and if the optimizer-specific hyperparameter definition is just a sequence `(lower_bound, upper_bound)`. This is a very widespread situation, so we already have the classes for that. Find them in in `SpecOnlyBoxes` module.
		* if it allows categorical variables. If it does, you need to define `_categorical` in `HyperparamsSpecsConverters`.
		* if it allows scalars. This influences `scalarMode:ScalarMetaMap` argument of `MSpec`:
			* `supportsScalars` - the optimizer deals with scalars in the spec itself.
			* `degenerateCategory` - the optimizer doesn't support scalars but supports categorical variables. The lib puts scalars into a degenerate category. May affect performance, if the impact is low this way is preferred because optimizers may have side effects like saving info to the disk.
			* `noScalars` - the optimizer doesn't support scalars and using categorical variables for them is infeasible: either not available or too big performance penalty. This causes scalars been saved into a separate dict and added back.
		* `isArray` - `True` if the spec is `Iterable`-based.
	* calling convention of a black-box function:
		* whether it is a `Mapping` (`dict`) or an `Iterable` (`list`, `tuple`, `ndarray`) or something else.
			* if it is a `Mapping`, you need specs with `hyperparamsVectorType` being derived from `HyperparamVector`
			* if it is an `Iterable`, you need specs with `hyperparamsVectorType` being derived from `HyperparamArray`
	* the argument controlling count of iterations. If there is no such a control, you can try to create a wrapper using an exception to break the loop.
	* the way the optimizer prints messages. All the messages in `invokeScoring` should be print via the `ProgressReporter` object passed. You may need some hacks if a lib directly uses `print` or an io stream. Please don't redefine global builtins like `print`.
2. Create a draft of a `Spec` using the info from the previous point, if it is needed. Inherit from the stuff resulted from call of `MSpec`.
3. Now you are ready to write the code of the backend. Inherit `GenericOptimizer` and populate the following properties of the class:
	* `specType` - is the type of your spec.
	* `__init__` - here you can save additional parameters of an optimizer
	* `prepareScoring` - here you can prepare your optimizer. You can save arbitrary context. This function returns a tuple `(countOfIterations, optimizerFriendlyName, context)`.
		* `countOfIterations` is for the case you need additional iterations. Usually you need to return `self.iters`.
		* `optimizerFriendlyName` is used in UI.
		* `context` is your context.
	* `invokeScoring(self, fn:typing.Callable, pb:ProgressReporter, context)` - actual optimization
		* `fn` is a prepared function. Accepts either array or dict depending on `self.__class__.specType.hyperparamsVectorType`
		* `pb` is a `ProgressReporter` object. You can use it for redirecting output and printing messages in the way not destructing the CLI progressbar.
		* `context` is your context.
		
		You usually wanna wrap a `fn` into an own function returning only mean. But try to return the whole tuple first, if it works fine, return the whole tuple. Tuples are compared lexicographically, so this way the values with the same mean but lower variance gonna be preferred by the optimizer.
	
4. Add it into `__init__.py`. Import the `Optimizer` subclass and add it to `Optimizers` class as a property, use a friendlier name if it is possible.
3. To test it open `tests\tests.py`, disable all the unneeded tests with `@unittest.skip`, enable `OptimizersTests.testOptimizer` and replace the optimizer name there with a friendlier name for your backend.
