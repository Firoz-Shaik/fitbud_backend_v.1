from dataclasses import dataclass
from app.models.user import User
from app.models.client import Client

@dataclass
class ClientContext:
    user: User
    client_profile: Client
    @property
    def id(self):
        return self.user.id


@dataclass
class TrainerContext:
    user: User
    @property
    def id(self):
        return self.user.id