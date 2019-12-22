#!/usr/bin/env python3

import typing
from . import *

from datetime import datetime
from pprint import pprint
from pathlib import Path
from dateutil.parser import parse as parseDate
from ruamel.yaml import YAML


mdIndent = " " * 4 # markdown doesn't support tabs as indent
firstJoiner = "\n" + mdIndent + "* "
secondJoiner = "\n" + mdIndent * 2 + "* "

def generateIssuesMessage(greetingMsg, stubIssues, ourMetaIssues):
	res = greetingMsg
	if stubIssues:
		res += firstJoiner + "KSY stub issues:"
		res += secondJoiner + secondJoiner.join(stubIssues)
	if ourMetaIssues:
		res += firstJoiner + "Additional metadata issues:"
		res += secondJoiner + secondJoiner.join(ourMetaIssues)
	return res

invalidLabel = "invalid"
validLabel = "info-provided"

def main():
	env = getGHEnv()
	gh = env["GITHUB"]
	inpV = env["INPUT"]
	e = json.loads(gh["EVENT_PATH"].read_text())
	#pprint(e)
	i = e["issue"]
	id = i["id"]
	no = i["number"]
	b = i["body"]
	l = i["locked"]
	c = parseDate(i["created_at"])
	up = parseDate(i["updated_at"])
	u = i["user"]
	r = e["repository"]
	rn = r["name"]
	ro = r["owner"]
	rol = ro["login"]
	lblz = {lbl["name"] for lbl in i["labels"]}

	#print(e["action"], "c", c, "up", up, u["login"], i["state"], lblz)
	ksyStub, otherMetadata = parseHeaders(b)

	parser = YAML(typ="safe")

	illF = " contains ill-formed YAML"
	if ksyStub:
		try:
			ksyStub = parser.load(ksyStub)
		except:
			ksyStub = None
			ksyStubIssues = ["KSY stub" + illF]
		if ksyStub:
			ksyStubIssues = lintKSYStub(ksyStub)
	else:
		ksyStubIssues = ["KSY stub (`meta` + `doc` + `doc-ref` must be present) is missing"]
	
	if otherMetadata:
		try:
			otherMetadata = parser.load(otherMetadata)
		except:
			otherMetadata = None
			additionalBlockIssues = ["Additional block" + illF]
		additionalBlockIssues = lintAdditionalBlock(otherMetadata)
	else:
		additionalBlockIssues = ()

	api = GHAPI(inpV["GITHUB_TOKEN"])
	repO = api.repo(rol, rn)
	issueO = repO.issue(no)

	if ksyStubIssues or additionalBlockIssues:
		lblzMustBe = (lblz | {invalidLabel}) - {validLabel}
		if invalidLabel not in lblz:
			issueO.leaveAComment(generateIssuesMessage("Hi. Thank you for leaving the request. Please, fix the following issues in it:", ksyStubIssues, additionalBlockIssues))
		else:
			# todo: parse the issues and diff them
			issueO.leaveAComment(generateIssuesMessage("Some issues are still present:", ksyStubIssues, additionalBlockIssues))
	else:
		lblzMustBe = (lblz | {validLabel}) - {invalidLabel}
		if invalidLabel in lblz or validLabel not in lblz:
			print("commenting")
			issueO.leaveAComment("The issues that are detected by the linter have been fixed. Thank you.")
			print("commented")
		else:
			pass  # everything is OK

	if lblzMustBe != lblz:
		print("Fixing labels")
		issueO.setLabels(lblzMustBe)
		print("Fixed labels")

	#pprint(ksyStub)
	#print(ksyStubIssues)
	#pprint(otherMetadata)

if __name__ == "__main__":
	main()
