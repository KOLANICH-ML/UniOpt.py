import typing

LossT = typing.Union[float, typing.Tuple[float, float]]
PointTupleT = typing.Tuple[dict, LossT]
PointsSequenceT = typing.Iterable[PointTupleT]


class Point(tuple):
	__slots__ = ()
	# broken
	#def __init__(self, pointTuple:PointTupleT):
	#	super(tuple, self).__init__(pointTuple)

	def __lt__(self, other: PointTupleT):
		return self[1] < other[1]

	def __le__(self, other: PointTupleT):
		return self[1] <= other[1]

	def __gt__(self, other: PointTupleT):
		return self[1] > other[1]

	def __ge__(self, other: PointTupleT):
		return self[1] >= other[1]

	@property
	def loss(self):
		return self[1]

	@property
	def params(self):
		return self[0]
