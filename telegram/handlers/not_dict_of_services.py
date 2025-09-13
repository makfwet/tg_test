from aiogram import Router, types
from telegram.filters.is_in_dict_of_services import IsInDictOfServices


router_not_dict_of_services = Router()
router_not_dict_of_services.callback_query.filter(IsInDictOfServices)