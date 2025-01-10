from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json

# with open("core/texts/text.json", "r", encoding="utf-8") as fh:
#     txt = json.load(fh)


async def btni(text, callback_data, adjust=None):  # 1 btn + n btns
    kb = InlineKeyboardBuilder()
    if type(text) is str:
        kb.button(text=text, callback_data=callback_data)
    else:
        x = int(len(text))
        i = 0
        while x != 0:
            kb.button(text=text[i], callback_data=callback_data[i])
            kb.row()
            x -= 1
            i += 1
        if adjust is not None:
            if len(text)!=1 and type(adjust) is int:
                adjust= list(map(int, "1"*len(text)))
            kb.adjust(*adjust)

    return kb.as_markup()


async def btni_static(data, mode=None, adjust=None):
    if mode is None:
        markup = await btni(data[0], data[1], adjust)
    elif mode == 'menu':
        markup = await btni(data[0][0], data[0][1], data[1])

    return markup



async def unpacker(data):
    texts = []
    funcs = []
    for i in data:
        texts.append(data[str(i)]['text'])
        funcs.append(data[str(i)]['cdata'])
    res = (texts, funcs)
    return res


async def un_btns(data, adjust=None):
    res = await unpacker(data)
    if adjust is None:
        adjust = list(map(int, "1"*len(res[0])))
    else:
        pass
    result = btni(res[0], res[1], adjust)
    return result


def markup_camelia(datasheet):
    buttons_names = list(datasheet["list"].keys())
    result = []
    for names in buttons_names:
        result.append((datasheet[names], names))
    main_button = datasheet["main_button"]

    return result


def genmarkup(data, special=None):    # передаём в функцию data dynamics в формате [(callback0, text0),...]
    kb = InlineKeyboardBuilder()
    if special is None:
        for dat in data:
            kb.button(text=f'{dat[1]}', callback_data=f"{dat[0]}")
    elif special == 1:
        for dat in data:
            kb.button(text=f'{dat[1]}', callback_data=f"{dat}")

    # if special == 'user':
    #     kb.button(text='В главное меню', callback_data="cmain")
    # elif special == "admin":
    #     kb.button(text='Админ меню', callback_data="admin_menu")
    # elif special == "admin_res":
    #     kb.button(text='Админ меню', callback_data="issues_mgmt_mode")
    kb.adjust(1)
    return kb.as_markup()

def itemtypeskb(data):
    kb = InlineKeyboardBuilder()
    for dat in data:
        kb.button(text=f'{dat[0]}', callback_data=f"{dat[0]}")
    kb.button(text='В главное меню', callback_data="seg_to_main_menu")
    kb.button(text='Новый тип товара', callback_data="item_type_add")
    kb.adjust(1)
    return kb.as_markup()

async def link_btn(caption, url):
    kb = InlineKeyboardBuilder()
    kb.button(text=caption, url=url)
    return kb.as_markup()

def gensbtns(data):
    kb = ReplyKeyboardBuilder()
    for dat in data:
        kb.button(text=dat, adjust=1)
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)


