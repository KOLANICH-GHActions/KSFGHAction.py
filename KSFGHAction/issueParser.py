import typing
import commonmark


def crawl(root, predicate: typing.Callable):
	for n, entered in root.walker():
		if predicate(n):
			yield n


def parseHeaders(text: str):
	parser = commonmark.Parser()
	parsed = parser.parse(text)

	def isSuitableCodeBlock(n):
		return n.t == "code_block" and n.info == "yaml"

	res = [b.literal for b in crawl(parsed, isSuitableCodeBlock)]
	if len(res) > 2:
		res1 = res[:2]
	elif len(res) < 1:
		return None, None
	elif len(res) == 1:
		return res[0], None
	return res
