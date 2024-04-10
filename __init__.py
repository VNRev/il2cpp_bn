from binaryninja import *

bv: BinaryView


class MyType():
    def __init__(self, bv: BinaryView, signature, isFunc=True):
        self.bv = bv
        self.initialize_typing_dict()
        if isFunc:
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
        self.args = " ".join(self.args)
        self.args = [arg.split() if len(arg.split()) > 1 else arg.split() + ['tem'] for arg in self.args.split(",")]
        self.args = [[arg[-1], " ".join(arg[:-1])] for arg in self.args]
        self.args = [(arg[0], self.string2type(arg[1])) for arg in self.args]

    def compile_funcType(self):
        self.funcType = Type.function(self.retType, self.args)

    def string2type(self, strIn):
        ptrNum = strIn.count("*")
        strIn = strIn.replace("*", "")
        strIn = strIn.strip()
        if " " in strIn:
            print("bug! space in strIn", self.signature)
            return self.dict1["uint64_t"]
        isPtr = "*" in strIn
        if strIn in self.dict1:
            ret = self.dict1[strIn]
        else:
            try:
                ret = Type.named_type_from_registered_type(self.bv, strIn)
            except:
                self.print_error(strIn)
                ret = self.dict1["uint64_t"]
        for i in range(ptrNum):
            ret = Type.pointer(self.bv.arch, ret)
        return ret

    def print_error(self, strIn):
        print("error type: ", strIn)
        print(self.signature)
        print(self.retType)
        print(self.name)
        print(self.args)


def get_addr(bv=None, addr=0):
    return bv.start + addr


def get_pointer(bv: BinaryView):
    return f"uint64_t"
    bv.arch.address_size


def set_name(bv, addr, name, isFunc=True):
    # 设置变量的名称
    if not isFunc:
        funcs = bv.get_functions_containing(addr)
        if funcs is not None:
            [bv.remove_user_function(x) for x in funcs]
        if bv.get_data_var_at(addr):
            bv.get_data_var_at(addr).name = name
        else:
            # 设置为char*
            bv.define_user_data_var(addr, Type.pointer(bv.arch, Type.char()), name)
        bv.set_comment_at(addr, name)
    else:
        # 设置函数的名称
        try:
            bv.get_functions_containing(addr)[0].name = name
        except:
            if addr != 0:
                print("set error", hex(addr), name)


def make_function(bv, start, end):
    # print(start)
    pos = start - 1
    funcset = set()

    while pos < end:
        try:
            pos = bv.get_next_function_start_after(pos)
            funcset.add(bv.get_functions_containing(pos)[0])
        except:
            pos += 1
            try:
                func = bv.get_functions_containing(pos)[0]
                if not func.name.startswith("sub_"):
                    return
                funcset.add(func)
            except:
                pass
    if len(funcset) != 1:
        for x in funcset:
            bv.remove_user_function(x)
    bv.create_user_function(start)


def apply_func_type(bv, addr, funcType: str):
    function_list = bv.get_functions_containing(addr)
    if not function_list:
        print("no function", hex(addr), funcType)
        return
    func = function_list[0]
    try:
        func.type = MyType(bv, funcType).funcType
    except Exception as e:
        funcType = funcType.replace("intptr_t method,", "")
        parserTmp = bv.parse_type_string(funcType)[0]
        func.type = parserTmp
        print("error type,use auto parser", funcType)
        print(e)


def apply_data_type(bv, addr, dataType: str):
    try:
        bv.get_data_var_at(addr).type = MyType(bv, dataType, False).string2type(dataType)
    except:
        print(f"error::{hex(addr)} {dataType}")


def make_ScriptString(bv: BinaryView, data=None):
    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "ScriptString" in data and "ScriptString" in processFields:
        index = 1
        scriptStrings = data["ScriptString"]
        for scriptString in scriptStrings:
            addr = get_addr(bv, addr=scriptString["Address"])
            value = scriptString["Value"]
            name = "StringLiteral_" + str(index)
            set_name(bv, addr, name, False)
            bv.set_comment_at(addr, value)
            index += 1
    print("ScriptString  finished!")


def make_ScriptMetadataMethod(bv: BinaryView, data=None):
    # 实际上是储存了method的地址的变量
    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "ScriptMetadataMethod" in data and "ScriptMetadataMethod" in processFields:
        scriptMetadataMethods: object = data["ScriptMetadataMethod"]
        for scriptMetadataMethod in scriptMetadataMethods:
            addr = get_addr(bv, addr=scriptMetadataMethod["Address"])  # 是变量的addr
            name = scriptMetadataMethod["Name"]
            methodAddr = get_addr(bv, addr=scriptMetadataMethod["MethodAddress"])
            set_name(bv, methodAddr, name, True)
            set_name(bv, addr, name, False)
            bv.set_comment_at(addr, f'{name} {hex(methodAddr)}')
    print("ScriptMetadataMethod finished!")


def make_ScriptMetadata_name(bv: BinaryView, data=None):
    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "ScriptMetadata" in data and "ScriptMetadata" in processFields:
        scriptMetadatas = data["ScriptMetadata"]
        for scriptMetadata in scriptMetadatas:
            addr = get_addr(bv, addr=scriptMetadata["Address"])
            name = scriptMetadata["Name"]
            set_name(bv, addr, name, False)
            if scriptMetadata["Signature"] is not None:
                signature = scriptMetadata["Signature"]
                bv.set_comment_at(addr, str(signature))
    print("ScriptMetadata-name  finished!")


def make_ScriptMethod_name(bv: BinaryView, data=None):
    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "ScriptMethod" in data and "ScriptMethod" in processFields:
        scriptMethods = data["ScriptMethod"]
        for scriptMethod in scriptMethods:
            addr = get_addr(bv, addr=scriptMethod["Address"])
            name = scriptMethod["Name"]
            set_name(bv, addr, name, True)
            if scriptMethod["Signature"] is not None:
                signature = scriptMethod["Signature"]
                bv.set_comment_at(addr, str(signature))
    print("ScriptMethod-name  finished!")


def make_ScriptMethod_type(bv: BinaryView, data=None):
    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "ScriptMethod" in data and "ScriptMethod" in processFields:
        scriptMethods = data["ScriptMethod"]
        for scriptMethod in scriptMethods:
            addr = get_addr(bv, addr=scriptMethod["Address"])
            if scriptMethod["Signature"] is not None:
                signature = scriptMethod["Signature"]
                apply_func_type(bv, addr, signature)
    print("ScriptMethod-type  finished!")


def make_ScriptMetadata_type(bv: BinaryView, data=None):
    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "ScriptMetadata" in data and "ScriptMetadata" in processFields:
        scriptMetadatas = data["ScriptMetadata"]
        for scriptMetadata in scriptMetadatas:
            addr = get_addr(bv, addr=scriptMetadata["Address"])
            if scriptMetadata["Signature"] is not None:
                signature = scriptMetadata["Signature"]
                apply_data_type(bv, addr, signature)
    print("ScriptMetadata-type finished!")


def make_func(bv: BinaryView, data=None):

    if data is None:
        import json
        path = get_open_filename_input("script.json")
        data = json.loads(open(path, 'rb').read().decode('utf-8'))
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
            start = get_addr(bv, addr=addresses[index])
            end = get_addr(bv, addr=addresses[index + 1])
            make_function(bv, start, end)
    if "ScriptMethod" in data and "ScriptMethod" in processFields:
        scriptMethods = data["ScriptMethod"]
        for scriptMethod in scriptMethods:
            addr = get_addr(bv, addr=scriptMethod["Address"])
            make_function(bv, addr, addr + 0x1)
    # if "ScriptMetadataMethod" in data and "ScriptMetadataMethod" in processFields:
    #     scriptMetadataMethods: object = data["ScriptMetadataMethod"]
    #     for scriptMetadataMethod in scriptMetadataMethods:
    #         addr = get_addr(bv, addr=scriptMetadataMethod["Address"])
    #         methodAddr = get_addr(bv, addr=scriptMetadataMethod["MethodAddress"])
    #         if bv.get_data_var_at(methodAddr) is None:
    #             make_function(bv, methodAddr, methodAddr + 0x1)
    #         if bv.get_data_var_at(addr) is None:
    #             make_function(bv, addr, addr + 0x1)
    print("make function finished!")


def all_recover(bv):
    import json
    path = get_open_filename_input("script.json")
    data = json.loads(open(path, 'rb').read().decode('utf-8'))
    # make_func(bv, data)
    # bv.update_analysis_and_wait()
    make_ScriptString(bv, data)
    make_ScriptMetadataMethod(bv, data)
    make_ScriptMetadata_name(bv, data)
    make_ScriptMethod_name(bv, data)
    make_ScriptMethod_type(bv, data)
    make_ScriptMetadata_type(bv, data)
    print("all recover finished!")


PluginCommand.register("il2cpp_bn\\1.make_func", "", make_func)
# PluginCommand.register("il2cpp_bn\\2.ScriptString", "", make_ScriptString)
# PluginCommand.register("il2cpp_bn\\3.ScriptMetadataMethod", "", make_ScriptMetadataMethod)
# PluginCommand.register("il2cpp_bn\\4.ScriptMetadata_name", "", make_ScriptMetadata_name)
# PluginCommand.register("il2cpp_bn\\5.ScriptMethod_name", "", make_ScriptMethod_name)
# PluginCommand.register("il2cpp_bn\\6.ScriptMethod_type", "", make_ScriptMethod_type)
# PluginCommand.register("il2cpp_bn\\7.ScriptMetadata_type", "", make_ScriptMetadata_type)
PluginCommand.register("il2cpp_bn\\2.recover Info", "", all_recover)
