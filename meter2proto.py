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
END_LIMIT_ROW_INDEX = 4
DATA_ROW_START_INDEX = 6
EXCEL_DIR = "excel"
IMPORT_DIR = "import"
IMPORT_EXT_DIR = "import-no-excel"
PROTO_DIR = "protobuf"
PROTO_EXT_DIR = "protobuf-ext"
OUTPUT_DIR = "output"
CONFIG_DIR = "."
CLIENT_CONFIG_DIR = "../assets/resources/configs"

INDEX_PROTO_TEMPLATE = """package proto;
__IMPORT_PROTOS__
"""
IMPORT_TEMPLATE = """
import "__CLASS_NAME__.proto";
"""
PROTO_TEMPLATE = """package proto;
message __CLASS_NAME__Item {__ITEM_STRUCT__
}
message __CLASS_NAME__{
	repeated __CLASS_NAME__Item items 	= 1;
}"""
ATTR_TEMPLATE = """
	optional __TYPE__ __ATTR__ 		= __INDEX__;"""
improtskey = "__IMPORT_PROTOS__"
structkey = "__ITEM_STRUCT__"
classkey = "__CLASS_NAME__"
typekey = "__TYPE__"
attrkey = "__ATTR__"
idxkey = "__INDEX__"

def mergeProtoFiles():
    os.system("node_modules\\.bin\\pbjs -t static-module -w commonjs -o pb-client.js protobuf/*.proto")
    with open("pb-client.js", "r", encoding='UTF-8') as f:
        toWrite = f.read()
    cocosContent = toWrite.replace('protobufjs/minimal', 'protobuf')
    with open("../assets/scripts/protobuf/pb-client.js", "w", encoding='UTF-8') as f:
        f.write(cocosContent)

if __name__ == "__main__":
	if os.path.exists(IMPORT_DIR):
		shutil.rmtree(IMPORT_DIR)
	shutil.copytree(IMPORT_EXT_DIR, IMPORT_DIR)
	if os.path.exists(OUTPUT_DIR):
		shutil.rmtree(OUTPUT_DIR)
	os.mkdir(OUTPUT_DIR)
	if os.path.exists(PROTO_DIR):
		shutil.rmtree(PROTO_DIR)
	shutil.copytree(PROTO_EXT_DIR, PROTO_DIR)

	imports = ""
	for xlr in os.listdir(EXCEL_DIR):
		if not xlr.endswith(".xls"):
			continue
		book = xlrd.open_workbook(os.path.join(EXCEL_DIR, xlr))
		sh = book.sheet_by_name("Sheet1")
		output_file_name = sh.row_values(0)[1]
		print("file name:", output_file_name)
		cnames = sh.row_values(NAME_ROW_INDEX)
		cendlimit = sh.row_values(END_LIMIT_ROW_INDEX)
		ctypes = sh.row_values(TYPE_ROW_INDEX)
		columns = []
		# gen proto
		struct = ""
		idx = 0
		for i in range(0, len(cendlimit)):
			if cendlimit[i].find("front") > -1:
				columns.append(i)
				idx = idx + 1
				attr = ATTR_TEMPLATE
				attr = attr.replace(typekey, ctypes[i])
				attr = attr.replace(attrkey, cnames[i])
				attr = attr.replace(idxkey, str(idx))
				struct = struct + attr
		proto_content = PROTO_TEMPLATE
		proto_content = proto_content.replace(structkey, struct)
		proto_content = proto_content.replace(classkey, output_file_name)
		with open(os.path.join(PROTO_DIR, output_file_name + ".proto"), "w") as f:
			f.write(proto_content)
		imp = IMPORT_TEMPLATE
		imp = imp.replace(classkey, output_file_name)
		imports = imports + imp

		jtxt = []
		for i in range(DATA_ROW_START_INDEX, sh.nrows):
			row = {}
			cells = sh.row(i)
			for j in range(0, len(columns)):
				attrType = ctypes[columns[j]]
				attrName = cnames[columns[j]]
				value = cells[columns[j]].value
				if attrType == "int32" or attrType == "int64":
					value = int(value)
				elif attrType == "float" or attrType == "double":
					value = float(value)
				elif attrType == "bool":
					value = bool(value)
				elif not isinstance(value, str):
					if isinstance(value, float) and attrType == "string":
						value = str(int(value))
				row[attrName] = value
			jtxt.append(row)
		with open(os.path.join(IMPORT_DIR, output_file_name + ".json"), "w") as f:
			# f.write(json.dumps(jtxt))
			f.write('{"items":' + json.dumps(jtxt) + '}')
		# # for editor
		# with open(os.path.join(OUTPUT_JS_DIR, output + ".js"), "w") as f:
		# 	f.write("module.exports = " + json.dumps(jtxt))
	#ext proto
	for protoExt in os.listdir(PROTO_EXT_DIR):
		imp = IMPORT_TEMPLATE
		imp = imp.replace(classkey, protoExt.split('.')[0])
		imports = imports + imp

	index_content = INDEX_PROTO_TEMPLATE
	index_content = index_content.replace(improtskey, imports)

	with open(os.path.join(PROTO_DIR, "index.proto"), "w") as f:
		f.write(index_content)

	mergeProtoFiles()

	os.system("node app.min.js")

	if os.path.exists(CLIENT_CONFIG_DIR):
		shutil.rmtree(CLIENT_CONFIG_DIR)
	shutil.copytree("output", CLIENT_CONFIG_DIR)
