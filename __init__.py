from binaryninja import *


class MyType():
    def __init__(self, bv: BinaryView, signature):
        self.bv = bv
        self.initialize_typing_dict()
        self.preprocess_signature(signature)
        self.parse_signature_tokens()
        self.compile_funcType()

    def initialize_typing_dict(self):
        self.dict1 = {"void": Type.void(),
                      "int8_t": Type.int(1), "int": Type.int(4),
                      "int16_t": Type.int(2), "int32_t": Type.int(4), "int64_t": Type.int(8),
                      "uint8_t": Type.int(1, False), "uint16_t": Type.int(2, False),
                      "uint32_t": Type.int(4, False), "uint64_t": Type.int(8, False),
                      "float": Type.float(4), "double": Type.float(8),
                      "long": Type.int(8), "bool": Type.bool(), "char": Type.char()}
        if self.bv.arch.address_size in (4, 8):
            self.dict1["intptr_t"] = Type.int(self.bv.arch.address_size)
            self.dict1["uintptr_t"] = Type.int(self.bv.arch.address_size, False)

    def preprocess_signature(self, signature):
        signature = signature.replace("intptr_t method,", "").replace("const ", "")
        self.tokens = signature.split()
        self.signature = signature

    def parse_signature_tokens(self):
        self.retType = self.string2type(self.tokens[0])
        self.name = self.tokens[1]
        self.args = [arg.replace("(", "").replace(");", "") for arg in self.tokens[2:]]
        self.args = [arg.split() if len(arg.split()) > 1 else arg.split() + ['tem'] for arg in self.args.split(",")]
        self.args = [[arg[-1], " ".join(arg[:-1])] for arg in self.args]
        self.args = [(arg[0], self.string2type(arg[1])) for arg in self.args]

    def compile_funcType(self):
        self.funcType = Type.function(self.retType, self.args)

    def string2type(self, strIn):
        strIn = strIn.replace("*", "")
        isPtr = "*" in strIn
        if strIn in self.dict1:
            ret = self.dict1[strIn]
        else:
            try:
                ret = Type.named_type_from_registered_type(self.bv, strIn)
            except:
                self.print_error(strIn)
                ret = self.dict1["uint64_t"]
        return Type.pointer(self.bv.arch, ret) if isPtr else ret

    def print_error(self, strIn):
        print("error type: ", strIn)
        print(self.signature)
        print(self.retType)
        print(self.name)
        print(self.args)


def applyTrue(bv: BinaryView):
    show_message_box("il2cpp_bn",
                     "use 'Import Header File' first!(import il2cpp.h \nand add\n '#define intptr_t int64_t  \n#define uintptr_t uint64_t' \n (x64))   \n then choose script.json",
                     MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.InformationIcon)
    import json
    path = get_open_filename_input("script.json")
    # path = "/Users/ltlly/Desktop/Il2CppDumper-win-v6.7.40 (1)/dump/script.json"
    # hpath = "/Users/ltlly/Desktop/Il2CppDumper-win-v6.7.40 (1)/dump/il2cpp.h"
    data = json.loads(open(path, 'rb').read().decode('utf-8'))

    def get_addr(addr):
        return bv.start + addr

    def set_name(addr, name):
        try:
            bv.get_functions_containing(addr)[0].name = name
        except IndexError:
            make_function(addr, addr + 1)
            bv.get_functions_containing(addr)[0].name = name
        except:
            print("set error", hex(addr), name)

    def make_function(start, end):
        funcset = set()
        for x in range(start, end):
            try:
                func = bv.get_functions_containing(x)[0]
                if not func.name.startswith("sub_"):
                    return
                funcset.add(func)
            except:
                pass
        if len(funcset) != 1:
            for x in funcset:
                bv.remove_user_function(x)
            bv.create_user_function(start)

    def apply_type(addr, funcType: str):
        func = None
        try:
            function_list = bv.get_functions_containing(addr)
            if not function_list:
                make_function(addr, addr + 1)
                function_list = bv.get_functions_containing(addr)
            func = function_list[0]
            func.type = MyType(bv, funcType).funcType
        except Exception:
            print(f"Error: {hex(addr)}, {funcType}")
            if func is not None:
                print(func.type)

    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]

    if "Addresses" in data and "Addresses" in processFields:
        addresses = data["Addresses"]
        for index in range(len(addresses) - 1):
            start = get_addr(addresses[index])
            end = get_addr(addresses[index + 1])
            make_function(start, end)

    if "ScriptMethod" in data and "ScriptMethod" in processFields:

        scriptMethods = data["ScriptMethod"]
        for scriptMethod in scriptMethods:
            addr = get_addr(scriptMethod["Address"])
            name = scriptMethod["Name"]
            set_name(addr, name)
            signature = scriptMethod["Signature"]
            apply_type(addr, signature)
            bv.set_comment_at(addr, str(signature))

    if "ScriptString" in data and "ScriptString" in processFields:
        index = 1
        scriptStrings = data["ScriptString"]
        for scriptString in scriptStrings:
            addr = get_addr(scriptString["Address"])
            value = scriptString["Value"]
            name = "StringLiteral_" + str(index)
            if bv.get_data_var_at(addr):
                bv.get_data_var_at(addr).name = name
                bv.set_comment_at(addr, str(value))
            else:
                bv.define_user_data_var(addr, "char*")
                bv.get_data_var_at(addr).name = name
                bv.set_comment_at(addr, str(value))
            index += 1

    if "ScriptMetadata" in data and "ScriptMetadata" in processFields:
        scriptMetadatas = data["ScriptMetadata"]
        for scriptMetadata in scriptMetadatas:
            addr = get_addr(scriptMetadata["Address"])
            name = scriptMetadata["Name"]
            set_name(addr, name)
            bv.set_comment_at(addr, str(name))
            if scriptMetadata["Signature"] is not None:
                signature = scriptMetadata["Signature"]
                apply_type(addr, signature)

    if "ScriptMetadataMethod" in data and "ScriptMetadataMethod" in processFields:
        scriptMetadataMethods: object = data["ScriptMetadataMethod"]
        for scriptMetadataMethod in scriptMetadataMethods:
            addr = get_addr(scriptMetadataMethod["Address"])
            name = scriptMetadataMethod["Name"]
            methodAddr = get_addr(scriptMetadataMethod["MethodAddress"])
            set_name(addr, name)
            bv.set_comment_at(addr, f'{name} {hex(methodAddr)}')
    print('Script finished!')


PluginCommand.register("il2cpp_bn\\import_info", "choose script.json to import info", applyTrue)
