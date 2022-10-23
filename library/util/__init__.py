from creart import add_creator

from library.util.frequency_limit import FrequencyLimitCreator
from library.util.module import ModulesCreator

add_creator(ModulesCreator)
add_creator(FrequencyLimitCreator)
