from binaryninja import *
from tqdm import tqdm


def do_nothing(bv):
    show_message_box("Do Nothing", "Congratulations! You have successfully done nothing.\n\n" +
                     "Pat yourself on the back.", MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.InformationIcon)


def apply_true(bv):
    show_message_box("il2cpp_bn", "use 'Import Header File' first!(import il2cpp.h \nand add\n '#define intptr_t int64_t  \n#define uintptr_t uint64_t' \n (x64))",
                     MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.InformationIcon)
    import json
    path = get_open_filename_input("script.json")
    hpath = get_open_filename_input("il2cpp.h")
    data = json.loads(open(path, 'rb').read().decode('utf-8'))

    # path = "/Users/ltlly/Desktop/Il2CppDumper-win-v6.7.40 (1)/dump/script.json"
    # hpath = "/Users/ltlly/Desktop/Il2CppDumper-win-v6.7.40 (1)/dump/il2cpp.h"

    def get_addr(addr):
        return bv.start + addr

    def set_name(addr, name):
        try:
            bv.get_functions_containing(addr)[0].name = name
        except:
            pass

    def make_function(start, end):
        funcset = {}
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

    def apply_type(addr, funcType):
        try:
            func = bv.get_functions_containing(addr)[0]
            func.type = funcType
        except:
            pass

    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]

    if "Addresses" in data and "Addresses" in processFields:
        addresses = data["Addresses"]
        for index in tqdm(range(len(addresses) - 1)):
            start = get_addr(addresses[index])
            end = get_addr(addresses[index + 1])
            make_function(start, end)

    if "ScriptMethod" in data and "ScriptMethod" in processFields:
        scriptMethods = data["ScriptMethod"]
        for scriptMethod in tqdm(scriptMethods):
            try:
                addr = get_addr(scriptMethod["Address"])
                name = scriptMethod["Name"]
                set_name(addr, name)
                signature = scriptMethod["Signature"]
                signature = signature.replace("intptr_t method,", "")
                apply_type(addr, bv.parse_type_string(signature)[0])
                bv.set_comment_at(addr, str(signature))
            except:
                print("error", hex(addr), signature)

    if "ScriptString" in data and "ScriptString" in processFields:
        index = 1
        scriptStrings = data["ScriptString"]
        for scriptString in tqdm(scriptStrings):
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
        for scriptMetadata in tqdm(scriptMetadatas):
            addr = get_addr(scriptMetadata["Address"])
            name = scriptMetadata["Name"]
            set_name(addr, name)
            bv.set_comment_at(addr, str(name))
            if scriptMetadata["Signature"] is not None:
                signature = scriptMetadata["Signature"]
                # bug    redefined method
                # error 0x53e944 void System_Action_object__StyleValues____ctor (System_Action_T1__T2__o* __this, Il2CppObject* object, intptr_t method, const MethodInfo_53E944* method);
                signature = signature.replace("intptr_t method,", "")
                apply_type(addr, bv.parse_type_string(signature)[0])

    if "ScriptMetadataMethod" in data and "ScriptMetadataMethod" in processFields:
        scriptMetadataMethods = data["ScriptMetadataMethod"]
        for scriptMetadataMethod in tqdm(scriptMetadataMethods):
            addr = get_addr(scriptMetadataMethod["Address"])
            name = scriptMetadataMethod["Name"]
            methodAddr = get_addr(scriptMetadataMethod["MethodAddress"])
            set_name(addr, name)
    print('Script finished!')


def apply_false(bv):
    show_message_box("il2cpp_bn", "use 'Import Header File' first!(import il2cpp.h \nand add\n '#define intptr_t int64_t  \n#define uintptr_t uint64_t' \n (x64))",
                     MessageBoxButtonSet.OKButtonSet, MessageBoxIcon.InformationIcon)
    import json
    path = get_open_filename_input("script.json")
    hpath = get_open_filename_input("il2cpp.h")
    data = json.loads(open(path, 'rb').read().decode('utf-8'))

    # path = "/Users/ltlly/Desktop/Il2CppDumper-win-v6.7.40 (1)/dump/script.json"
    # hpath = "/Users/ltlly/Desktop/Il2CppDumper-win-v6.7.40 (1)/dump/il2cpp.h"

    def get_addr(addr):
        return bv.start + addr

    def set_name(addr, name):
        try:
            bv.get_functions_containing(addr)[0].name = name
        except:
            pass

    def make_function(start, end):
        funcset = {}
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

    def apply_type(addr, funcType):
        try:
            func = bv.get_functions_containing(addr)[0]
            func.type = funcType
        except:
            pass

    processFields = [
        "ScriptMethod",
        "ScriptString",
        "ScriptMetadata",
        "ScriptMetadataMethod",
        "Addresses",
    ]
    if "Addresses" in data and "Addresses" in processFields:
        addresses = data["Addresses"]
        for index in tqdm(range(len(addresses) - 1)):
            start = get_addr(addresses[index])
            end = get_addr(addresses[index + 1])
            make_function(start, end)

    if "ScriptMethod" in data and "ScriptMethod" in processFields:
        scriptMethods = data["ScriptMethod"]
        for scriptMethod in tqdm(scriptMethods):
            try:
                addr = get_addr(scriptMethod["Address"])
                name = scriptMethod["Name"]
                set_name(addr, name)
                signature = scriptMethod["Signature"]
                signature = signature.replace("intptr_t method,", "")
                # apply_type(addr, bv.parse_type_string(signature)[0])
                bv.set_comment_at(addr, str(signature))
            except:
                print("error", hex(addr), signature)

    if "ScriptString" in data and "ScriptString" in processFields:
        index = 1
        scriptStrings = data["ScriptString"]
        for scriptString in tqdm(scriptStrings):
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
        for scriptMetadata in tqdm(scriptMetadatas):
            addr = get_addr(scriptMetadata["Address"])
            name = scriptMetadata["Name"]
            set_name(addr, name)
            bv.set_comment_at(addr, str(name))
            if scriptMetadata["Signature"] is not None:
                signature = scriptMetadata["Signature"]
                # bug    redefined method
                # error 0x53e944 void System_Action_object__StyleValues____ctor (System_Action_T1__T2__o* __this, Il2CppObject* object, intptr_t method, const MethodInfo_53E944* method);
                signature = signature.replace("intptr_t method,", "")
                # apply_type(addr, bv.parse_type_string(signature)[0])

    if "ScriptMetadataMethod" in data and "ScriptMetadataMethod" in processFields:
        scriptMetadataMethods = data["ScriptMetadataMethod"]
        for scriptMetadataMethod in tqdm(scriptMetadataMethods):
            addr = get_addr(scriptMetadataMethod["Address"])
            name = scriptMetadataMethod["Name"]
            methodAddr = get_addr(scriptMetadataMethod["MethodAddress"])
            set_name(addr, name)
    print('Script finished!')


PluginCommand.register("il2cpp_bn\\import_info", "import_info", apply_true)
PluginCommand.register("il2cpp_bn\\import_info(no struct)",
                       "import_info(no struct)", apply_false)
