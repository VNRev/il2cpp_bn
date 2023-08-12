# il2cppdumper 2 bn

将il2cppdumper的符号信息导入binaryninja中，就像使用其自带的脚本导入ida中一样

实现了

更改函数名称及声明 并将声明自动注释
![Alt text](image.png)

导入string并注释

![Alt text](image-1.png)


# 使用方法

先使用il2cpp获取script.json和il2cpp.h

在il2cpp.h的头部增加

(64位)
```
#define intptr_t int64_t
#define uintptr_t uint64_t
```

然后使用bn的内置功能 ctrl+p  搜索 'Import Header File'

导入il2cpp.h

然后使用插件 
选择script.json
再选择il2cpp.h

等待即可


# 不足

1.太慢啦

涉及到bv.parse_type_string(signature)时会非常慢

在不更改函数声明时只需要数分钟 （使用no struct选项

而更改函数声明时需要数个小时 （macbook air m1

在此期间会完全无响应 （导致加的进度条无效


2.没有找到自动导入头文件的api函数 只能手动导入


