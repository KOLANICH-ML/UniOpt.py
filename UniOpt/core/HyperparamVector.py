import typing


class HyperparamVector:
	"""A container class storing the functions for transforming hyperparams CONTAINER TYPE (dict, list) back and forth."""

	makeEmpty = staticmethod(dict)
	primitiveType = dict

	@classmethod
	def dict2native(cls, dic: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		"""Transforms a dict into an object of native output type of a spec"""
		return dic

	@classmethod
	def native2dict(cls, native: typing.Dict[str, typing.Any], spec) -> typing.Dict[str, typing.Any]:
		"""Transforms an object of native output type into a dict of a spec"""
		return native
