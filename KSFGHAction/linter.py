import typing
import re
from urllib.parse import urlparse

from .validator import *
from .utils import *

idRxText = "[a-z][\\da-z_]*[\\da-z]"
idRx = re.compile(idRxText)


class metaMandatory(metaclass=ClassDictMeta):
	def id(v, issues):
		if not idRx.match(v):
			issues.append("`id` must match `" + idRxText + "` regexp")

	def title(v, issues):
		pass


class rootLevelMandatory(metaclass=ClassDictMeta):
	meta = (metaMandatory, {})

	def doc(v, issues):
		pass


def validateDocRef(v, issues):
	if isinstance(v, str):
		v = [v]
	if not isinstance(v, list):
		issues.append("`doc-ref` must be either a string or an array of strings")
		return
	for i, s in enumerate(v):
		if not isinstance(s, str):
			issues.append(str(i) + " element of `doc-ref` must be a string (currently " + repr(type(s).__name__) + ")")
			continue


rootLevelMandatory["doc-ref"] = validateDocRef


def lintKSYStub(stub) -> typing.Iterable[str]:
	issues = []
	validate(stub, rootLevelMandatory, {}, issues)
	return issues


class additionalBlockSchema(metaclass=ClassDictMeta):
	def WiP(v, issues):
		if isinstance(v, str):
			v = [v]
		if not isinstance(v, list):
			issues.append("`WiP` must be either a string or an array of strings")
			return
		for i, s in enumerate(v):
			if not isinstance(s, str):
				issues.append(str(i) + " element of `WiP` must be a string (currently " + repr(type(s).__name__) + ")")
				continue
			try:
				urlparse(s)
			except:
				issues.append(str(i) + " element of `WiP` must be a valid URI")


def lintAdditionalBlock(block) -> typing.Iterable[str]:
	issues = []
	validate(block, {}, additionalBlockSchema, issues)
	return issues


def lint(b, currentLabelDtor, react):
	ksyStub, otherMetadata = parseHeaders(b)

	parser = YAML(typ="safe")

	illF = " contains ill-formed YAML"
	if ksyStub:
		try:
			ksyStub = parser.load(ksyStub)
		except:
			ksyStub = None
			react.issues = ["KSY stub" + illF]
		if ksyStub:
			react.issues += lintKSYStub(ksyStub)
	else:
		react.issues = ["KSY stub (`meta` + `doc` + `doc-ref` must be present) is missing"]
	
	if otherMetadata:
		try:
			otherMetadata = parser.load(otherMetadata)
		except:
			otherMetadata = None
			additionalBlockIssues = ["Additional block" + illF]
		react.issues += lintAdditionalBlock(otherMetadata)
	else:
		pass
