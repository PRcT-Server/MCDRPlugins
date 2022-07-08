from operator import or_
from uuid import UUID

import hjson as json
from nbt.nbt import NBTFile
from sqlalchemy import (Boolean, Column, Integer, MetaData, String,
                        create_engine, or_)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from player_manager import stored
from player_manager.config import Config

Base = declarative_base()
engine = create_engine('sqlite:///./PlayerManager.db?check_same_thread=False&timeout=20') 
metaData = MetaData(engine)
session = Session(engine)

class Player(Base):
    __tablename__ = "player"
    id = Column(Integer(), primary_key=True)
    name = Column(String(length=64), unique=True)
    uuid = Column(String(length=128), unique=True)
    nick_name = Column(String(length=128))
    auto_replase = Column(Boolean(), default=0)
    joined_time = Column(Integer())

    def __repr__(self) -> str:
        return str(self.name)
    
    def is_onlineUUID(self):
        if UUID(self.uuid).version == 4:
            return True
        return False

    def get_stats(self):
        try:
            with open(Config().get_world_path() + f"/stats/{self.uuid}.json") as file:
                stats = json.load(file)
        except Exception as e:
            stored.serverInterface.logger.error(e)
            return None

        return stats["stats"]

    def get_data(self):
        dataApi = stored.serverInterface.get_plugin_instance("minecraft_data_api")
        data = {}

        if self.name in dataApi.get_server_player_list()[-1]:
            data = dataApi.get_player_info(self.name)
        else:
            data = NBTFile(Config().get_world_path()+f"/playerdata/{self.uuid}.dat")
        
        return data

    def get_info(self) -> list:
        data = self.get_data()
        x = float(str(data["Pos"][0]))
        y = float(str(data["Pos"][1]))
        z = float(str(data["Pos"][2]))
        x1 = float(str(data["Rotation"][0]))
        y1 = float(str(data["Rotation"][1]))
        dim = str(data["Dimension"])

        location = f'[x:{int(x)},y:{int(y)},z:{int(z)},dim:"{dim}"]'
        command = f"/player {self.name} spawn at {x} {y} {z} facing {x1} {y1} in {dim}"
        return [location, command]
    
    @staticmethod
    def get_player(name:str) -> "Player":
        player = session.query(Player).filter(Player.name == name).order_by(Player.name).first()
        return player
    
    @staticmethod
    def get_players(page:int):
        players = session.query(Player).order_by(Player.name).limit(stored.config.query_limit).offset((page - 1)*stored.config.query_limit).all()
        return players
    
    @staticmethod
    def search_player(keyword:str, page:int) -> list["Player"]:
        players = session.query(Player).filter(or_(Player.name.like("%"+keyword+"%"), Player.nick_name.like("%"+keyword+"%"))).order_by(Player.name).limit(
            stored.config.query_limit).offset((page - 1)*stored.config.query_limit)
        return players

    @staticmethod
    def get_online_players(page:int) -> list["Player"]:
        dataApi = stored.serverInterface.get_plugin_instance("minecraft_data_api")
        onlinePlayers = dataApi.get_server_player_list()[-1]
        players = session.query(Player).filter(Player.name.in_(onlinePlayers)).order_by(Player.name).limit(
            stored.config.query_limit).offset((page - 1)*stored.config.query_limit).all()
        return players
    
    @staticmethod
    def get_nick_players(page:int) -> list["Player"]:
        players = session.query(Player).filter(Player.nick_name != None).order_by(Player.name).limit(
            stored.config.query_limit).offset((page - 1)*stored.config.query_limit).all()
        return players
            
def creat_database():
    Base.metadata.create_all(engine)
