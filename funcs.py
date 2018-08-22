import numpy as np


def modRosenbrockNP(X, a=1, b=100):
	return np.sqrt(np.power(a - X[0], 4) + b * np.power(X[1] - np.power(X[0], 2), 2))


def ackleyRosenbrockNp(X, a=20, b=0.2, c=2 * np.pi):
	return np.real(a * (1 - np.exp(-b * np.sqrt(modRosenbrockNP(X, a=0, b=a) / X.shape[0]))) - np.exp(np.sum(np.cos(c * X), axis=0) / X.shape[0]) + np.exp(1))


def ackleyRosenbrock(params):
	"""Ackley function"""
	X = np.array(list(params.values()))
	return ackleyRosenbrockNp(X)


def ackleyRosenbrockWithVariance(params):
	return (ackleyRosenbrock(params), 0)


def logoFunc(X):
	return ackleyRosenbrockNp(np.array((np.sinh(X[0]), X[1])))
