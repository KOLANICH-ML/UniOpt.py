import typing


class MetaMapMeta(type):
	def __new__(cls, className: str, parents, attrs: typing.Dict[str, typing.Any], *args, **kwargs) -> typing.Type["MetaMap"]:
		defaultCase = None
		newAttrs = type(attrs)()
		newAttrs["_namePartToClassMapping"] = {}
		newAttrs["_classToNamePartMapping"] = {}
		for friendlyName, v in attrs.items():
			if friendlyName[0] == "_":
				newAttrs[friendlyName] = v
				continue

			if v is None or isinstance(v, type):
				defaultCase = v
			else:
				(namePart, mixinCls) = v
				newAttrs["_namePartToClassMapping"][namePart] = mixinCls
				newAttrs["_classToNamePartMapping"][mixinCls] = namePart
				newAttrs[friendlyName] = mixinCls

		newAttrs["_namePartToClassMapping"][None] = defaultCase
		newAttrs["__slots__"] = tuple()
		return super().__new__(cls, className, parents, newAttrs, *args, **kwargs)


class MetaMap(object, metaclass=MetaMapMeta):
	def __new__(cls):
		raise NotImplementedError("These classes are not meant to be instantiated!")
