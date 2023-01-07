from typing import Literal

from graia.ariadne.model import Friend, Group, Member, Stranger

Sender = Member | Friend | Stranger
"""发信人"""

Field = Group | Literal[0]
"""聊天区域"""
