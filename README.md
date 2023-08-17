# 中文

## il2cpp_bn

将il2cppdumper的符号信息导入binaryninja中，就像使用其自带的脚本导入ida中一样

实现了

更改函数名称及声明 并将声明自动注释
![Alt text](image.png)

导入string并注释

![Alt text](image-1.png)

## 使用方法

先使用il2cpp获取script.json和il2cpp.h

在il2cpp.h的头部增加

(64位)

```
#define intptr_t int64_t
#define uintptr_t uint64_t
```

然后使用bn的内置功能 ctrl+p  搜索 'Import Header File'

导入il2cpp.h

然后使用插件,选择对应的功能或all_recover即可
选择script.json

等待即可

## 不足

1.没有找到自动导入头文件的api函数 只能手动导入

## 感谢

感谢 @mFallW1nd 提供的优化思路，通过手动parser，获取type的方式避免了使用bv.parse_types_from_string的性能问题

# English

The original language is Chinese. Machine translation is used below.

## il2cpp_bn

Import the symbol information of il2cppdumper into binaryninja as if it were imported into ida using its own script

Realized

Change the function name and declaration and automatically comment the declaration
![Alt text](image.png)

Import string and comment

![Alt text](image-1.png)

## Usage

use il2cpp to get script.json and il2cpp.h

Add to the top of il2cpp.h

(x64)

```
#define intptr_t int64_t
#define uintptr_t uint64_t
```

Then search for 'Import Header File' using ctrl+p

import il2cpp.h

Then use the plug-in
Select script.json
Just wait.

## Deficiency

1. The api function that cannot find the automatic import header file can only be imported manually.

## contribute

Thanks to the optimization ideas provided by @ mFallW1nd, the way of obtaining type through manual parser avoids the performance problems of using bv.parse_types_from_string
