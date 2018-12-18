# -*- coding:utf-8 -*-f
# run with python v3.0+
# created by Fang tianlei

import os
import sys
import shutil
import xlrd
import json

NAME_ROW_INDEX = 2
TYPE_ROW_INDEX = 5
DATA_ROW_START_INDEX = 6
EXCEL_DIR = "excel"
OUTPUT_DIR = "output"
CONFIG_DIR = "."

if __name__ == "__main__":
	if os.path.exists(OUTPUT_DIR):
		shutil.rmtree(OUTPUT_DIR)
	os.mkdir(OUTPUT_DIR)

	for xlr in os.listdir(CONFIG_DIR):
		if xlr.endswith(".conf"):
			print("TABLE: ",xlr)
			f = open(xlr, "r", encoding="UTF-8")
			conf = json.load(f)
			f.close()
			sheet = None
			excel = None
			output = None
			rows = None
			if "excel" in conf:
				excel = conf["excel"]
				print("EXCEL: ",conf["excel"])
			else:
				print("ERROR. no excel")
				quit()
			if "sheet" in conf:
				sheet = conf["sheet"]
				print("SHEET: ",conf["sheet"])
			else:
				print("ERROR. no sheet")
				quit()
			if "output" in conf:
				output = conf["output"]
			else:
				print("ERROR. no output")
				quit()
			if "rows" in conf:
				rows = conf["rows"]
			else:
				print("ERROR. no rows")
				quit()
		else:
			continue

		book = xlrd.open_workbook(os.path.join(EXCEL_DIR, excel))
		sh = book.sheet_by_name(sheet)
		cnames = sh.row_values(NAME_ROW_INDEX)
		ctypes = sh.row_values(TYPE_ROW_INDEX)
		print("NAMES: ", cnames)
		for i in range(0, len(rows)):
			if rows[i]["name"] in cnames:
				rows[i]["index"] = cnames.index(rows[i]["name"])
				rows[i]["type"] = ctypes[rows[i]["index"]]
			else:
				print("ERROR. no row: ", rows[i]["name"])
				quit()

		jtxt = []
		for i in range(DATA_ROW_START_INDEX, sh.nrows):
			row = []
			cells = sh.row(i)
			for j in range(0, len(rows)):
				value = cells[rows[j]["index"]].value
				if rows[j]["type"] == "int":
					value = int(value)
				elif rows[j]["type"] == "float" or rows[j]["type"] == "double":
					value = float(value)
				elif rows[j]["type"] == "boolean":
					value = bool(value)
				elif not isinstance(value, str):
					if isinstance(value, float) and rows[j]["type"] == "string":#为了解决excel格式设置错误的问题
						value = str(int(value))
				row.append(value)
			jtxt.append(row)
		with open(os.path.join(OUTPUT_DIR, output + ".json"), "w") as f:
			f.write(json.dumps(jtxt))

