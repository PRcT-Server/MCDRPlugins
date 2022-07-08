import re
from time import localtime, strftime, time

from mcdreforged.api.all import *

from player_manager import stored
from player_manager.config import Config
from player_manager.model import Player, creat_database, session
from player_manager.util import get_uuid


def on_load(server: PluginServerInterface, old):
    stored.serverInterface = server
    stored.config = server.load_config_simple("config.json",in_data_folder=True, target_class=Config)
    Config.set_instance(stored.config)

    creat_database()

    server.register_help_message(stored.config.prefix, "PlayerManager 使用指北")
    server.register_command(Literal(stored.config.prefix).runs(send_help)
        .then(
            Literal("list").runs(send_list)
            .then(Literal("online").runs(lambda src:send_list(src, True))
                .then(Integer("page").runs(lambda src,ctx:send_list(src, True, page=ctx["page"]))))
            .then(Literal("tag").runs(lambda src:send_list(src, haveTag=True))
                .then(Integer("page").runs(lambda src,ctx:send_list(src, haveTag=True, page=ctx["page"]))))
            .then(Integer("page").runs(lambda src,ctx:send_list(src, page=ctx["page"]))))
        .then(
            Literal("search")
            .then(QuotableText("keyword").runs(lambda src,ctx: send_list(src, key=ctx["keyword"], page=1))
                .then(Integer("page").runs(lambda src,ctx:send_list(src,page=ctx["page"],key=ctx["keyword"])))))

        .then(QuotableText("player").runs(lambda src, ctx:send_info(src, ctx["player"]))
            .then(Literal("set")
                .then(QuotableText("nickname").runs(lambda src,ctx:set_nick(src, ctx["player"], ctx["nickname"]))))
            .then(Literal("auto").runs(lambda src,ctx: set_auto(src, ctx["player"]))))        
    )

def on_server_startup(server:PluginCommandSource):
    auto_replase(server)

def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    join_update(server, player, info)

@new_thread("PlayerManager")
def join_update(server: PluginServerInterface, player: str, info: Info):
    result = re.match(r"(\w+)\[([0-9\.\:\/]+|local)\] logged in with entity id", info.content)
    if result is None or result.group(2) != "local":
        return
    thisPlayer = Player.get_player(player)
    if not thisPlayer:
        newPlayer = Player(
            name = player,
            uuid = get_uuid(player),
            joined_time = int(time())
        )
        session.add(newPlayer)
        session.commit()
    
def send_help(src: CommandSource):
    prefix = stored.config.prefix
    msg = f'''
    ------------§aCommand Useage§r---------------
    | {prefix} - 显示这条帮助命令
    | {prefix} list *<page> - 列出Bot
    | {prefix} list tag *<page> - 列出拥有备注的Bot
    | {prefix} list online *<page> - 列出在线Bot
    | {prefix} search <keyWord> *<page> - 搜索Bot
    | {prefix} <name> set <rename> - 设置Bot的备注
    | {prefix} <name> auto - 设置BOT的自动重新放置
    | {prefix} <name> - 查询BOT的详细信息
    '''
    src.reply(msg)

@new_thread("PlayerManager")
def send_list(src:CommandSource, online:bool = False, haveTag:bool = False, page:int = 1, key:str = ""):
    if online:
        players = Player.get_online_players(page)
        ctx = "list online"
    elif haveTag:
        players = Player.get_nick_players(page)
        ctx = "list tag"
    elif key:
        players = Player.search_player(key,page)
        ctx = f"search {key}"
    else:
        players = Player.get_players(page)
        ctx = "list"

    if not players:
        src.reply("没有数据捏")

    for player in players:
        name = player.name if not haveTag else player.nick_name
        if key:
            name = player.nick_name if player.nick_name is not None else player.name
        info = player.get_info()
        reply = RTextList(
            RText(f"{name}:").set_click_event(RAction.run_command, f"{stored.config.prefix} {player.name}"),
            RText(info[0]).set_color(RColor.green),
            RText(" "),
            RText("[U]").set_click_event(RAction.run_command, f"/player {player.name} use")
                .set_hover_text("使用这个BOT"),
            RText(" "),
            RText("[R]").set_click_event(RAction.run_command, info[-1])
                .set_hover_text("在BOT的下线位置重新生成BOT"),
            RText(" "),
            RText("[C]").set_click_event(RAction.run_command, f"/player {player.name} use continuous")
                .set_hover_text("持续使用这个BOT"),
            RText(" "),
            RText("[X]").set_click_event(RAction.run_command, f"/player {player.name} kill")
                .set_hover_text("做 掉这个BOT").set_color(RColor.red)
        )
        src.reply(reply)

    src.reply(RTextList(
        RText("<<").set_click_event(RAction.run_command, f"{stored.config.prefix} {ctx} {page - 1}"),
        RText(f" {page} "),
        RText(">>").set_click_event(RAction.run_command, f"{stored.config.prefix} {ctx} {page + 1}")
    ))

def send_info(src:CommandSource, name:str):
    player = Player.get_player(name)
    if player is None:
        src.reply("找不到此玩家")
        return
    rtexts = [
        RText("----------"),
        RTextList(
            RText(f"{name}").set_hover_text(f"UUID: {player.uuid}\n是否为正版: {player.is_onlineUUID()}"),
            RText(" "),
            RText(f"备注: {player.nick_name}")
        ),
        RText(f"是否自动重新生成: {player.auto_replase}"),
        RText("首次加入时间:{}".format(strftime("%Y-%m-%d %H:%M:%S", localtime(player.joined_time)))),
        RText("----------")
    ]
    for rtext in rtexts:
        src.reply(rtext)

def set_nick(src:CommandSource, name:str, nick_name:str):
    player = Player.get_player(name)
    if player is not None:
        player.nick_name = nick_name
        session.commit()
        src.reply(f"已经将{name}的备注设置为{nick_name}")
    else:
        src.reply("设置失败，找不到此BOT")

def set_auto(src:CommandSource, name:str):
    player = Player.get_player(name)
    if player is not None:
        player.auto_replase = not player.auto_replase
        session.commit()
        src.reply(f"{name}的自动重新生成已经被设置为{not player.auto_replase}")
    else:
        src.reply("设置失败！")
    
@new_thread("PlayerManager")
def auto_replase(server: PluginServerInterface):
    players = session.query(Player).filter(Player.auto_replase).all()
    for player in players:
        server.execute(player.get_info()[-1])


        
