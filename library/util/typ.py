from typing import Literal

from graia.ariadne.model import Friend, Group, Member, Stranger

Sender = Member | Friend | Stranger
"""发信人"""

SenderWide = Sender | int
"""发信人宽泛类型"""

Field = Group | Literal[0]
"""聊天区域"""

FieldWide = Field | int
"""聊天区域宽泛类型"""
