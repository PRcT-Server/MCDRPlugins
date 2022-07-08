import os

from mcdreforged.api.utils.serializer import Serializable

class Config(Serializable):
    prefix: str = "!!pm"
    server_path: str = './server'
    world_folder: str = 'world'
    query_limit: int = 10
    auto_bot_replase: bool = False

    __instance: 'Config' = None

    def get_world_path(self):
        return os.path.join(self.server_path, self.world_folder)

    @classmethod
    def set_instance(cls,ins:'Config'):
        cls.__instance = ins
    
    @classmethod
    def get_instance(cls):
        return cls.__instance
    


    
