# PlayerManager
> 方便，快捷地管理你的地毯端假人!   
 
PS：本插件适用于MCDR 2x 
#### 插件依赖：    
* [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) 数据库模块
* [hjson](https://pypi.org/project/hjson/) 比 Python标准库更快的 Json解析
* [nbt](https://pypi.org/project/NBT/) 读取 Minecraft原版 Tag

#### 插件配置

```
{
    "prefix": "!!pm",             # 调用 PlayerManager所使用的命令
    "server_path": "./server",    # 服务器路径和 MCDR运行路径的相对路径，一般不变
    "world_folder": "world",      # 服务器存档文件夹名称，一般不变
    "query_limit": 10,            # 每次查询最多显示的 BOT数量
    "auto_bot_replase": false     # Debug选项，不用管
}
```

### 插件使用

```!!pm - 查看插件使用帮助```

```!!pm list *<页码> ``` - 查看服务器的假人列表

```!!pm list tag *<页码> ``` - 查看备注假人列表

```!!pm list online *<页码> ``` - 查看在线假人列表

```!!pm search <关键词> *<page>``` - 通过假人名和假人备注查找假人 

```!!pm <假人名> set <备注> ``` - 为假人设置备注

```!!pm <假人名> auto``` - 设置假人在每次服务器重启以后自动重新生成，再次使用为取消设置

```!!pm <假人名>``` - 查看假人的设置信息

