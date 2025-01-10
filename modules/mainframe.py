import os
import json
import hashlib
from datetime import datetime
from uuid import uuid4

class Settings:
    useModules = True
    check_SHA256 = False
    DebugLevel = 0

    def modules_list(self):
        print("Сюда сунем запросник к базе модулей")


def checksumm(setup_sha256, path):
    hash = hashlib.sha256()
    with open(f"{path}", "rb") as file:
        hash.update(file.read())
    if hash.hexdigest() == setup_sha256:
        return True
    else:
        if not Settings.check_SHA256:
            return True
        return False


def get_exsisted_modules_and_shas():
    try:
        with open(f"mods/modules_data.json", "r") as f:
            modules_data = json.load(f)
        modules_names = list(modules_data["modules"].keys())
        modules_shas_dict = {}
        for names in modules_names:
            modules_shas_dict[modules_data["modules"][names]["module_hash_sha256"]] = names
        return modules_shas_dict, modules_names
    except:
        return None


def import_module(new_data):
    with open(f"mods/modules_data.json", "r") as f:
        modules_data = json.load(f)

    name = str((list(new_data.keys()))[0])
    modules_data["modules"][name] = new_data[name]
    if Settings.DebugLevel > 1:
        print("PRE DUMP", modules_data)
    with open(f"mods/modules_data.json", "r+") as fss:
         json.dump(modules_data, fss)


def pre_import_module(new_data):
    block = {
        "modules": {}
    }

    try:
        with open(f"mods/modules_data.json", "r") as f:
            modules_data = json.load(f)
    except:
        if Settings.DebugLevel > 0:
            print("READ ERROR ON PRE IMPORT. CLEARING: modules_data.json ")
        if not os.path.exists("mods/modules_data.json"):
            if Settings.DebugLevel > 0:
                print("NO MODULE FILE: modules_data.json ")
            mode = "w"
        else:
            mode = "r+"

        with open("mods/modules_data.json", mode) as fs:
            json.dump(block, fs)
    import_module(new_data)


def build_module_frame(settings):
    try:
        try:
            example = {
                f"{settings['module_name']}": {
                    "module_id": f"{uuid4()}",
                    "module_dt_integrated": f"{datetime.now()}",
                    "module_integrated_name": f"{settings['module_integrated_name']}",
                    "module_description": f"{settings['module_description']}",
                    "module_hash_sha256": f"{settings['module_hash_sha256']}"
                }
            }
            if Settings.DebugLevel > 1:
                print(example)
        except:
            if Settings.DebugLevel > 0:
                print("Ошибка при во время сборки фрейма")
            quit()
        try:
            pre_import_module(example)
            return True
        except:
            if Settings.DebugLevel > 0:
                print("Ошибка во время импорта")
    except:
        return False


def frame_worker(msha256, sp, module_json):
    if checksumm(setup_sha256=msha256,
                 path=f"mods/{sp}/{module_json['module']['module_integrated_name']}"):
        if build_module_frame(module_json["module"]):
            if Settings.DebugLevel > -1:
                print(f'[MODULES][{sp}] Модуль успешно импортирован')
        else:
            if Settings.DebugLevel > -1:
                print(f'[MODULES][{sp}] Ошибка импорта модуля')

    else:
        if Settings.DebugLevel > -1:
            print(f'[MODULES][{sp}] Ошибка контрольной суммы')


def master_module_integrator():
    if not Settings.check_SHA256:
        if Settings.DebugLevel > -1:
            print("[MODULES] Отключена проверка контрольной суммы")
    spx = []
    for mld in os.listdir('mods'):
            if os.path.isdir(s=f'mods/{mld}'):
                spx.append(mld)

    for sp in spx:
        try:
            with open(f"mods/{sp}/settings.json", "r") as settings:
                module_json = json.load(settings)

            msha256 = module_json['module']['module_hash_sha256']
            exsisted_modules = get_exsisted_modules_and_shas()
            if exsisted_modules is None:
                frame_worker(msha256, sp, module_json)
            else:
                if msha256 in list(exsisted_modules[0].keys()):
                    if Settings.DebugLevel > -1:
                        print(f'[MODULES][{sp}] Модуль уже импортирован с именем {exsisted_modules[0][msha256]}')
                    # quit(code=f'[MODULES][{sp}] Модуль уже импортирован с именем {exsisted_modules[msha256]}')
                elif module_json["module"]["module_name"] in exsisted_modules[1]:
                    if Settings.DebugLevel > 1:
                        print(exsisted_modules)

                    if Settings.DebugLevel > -1:
                        print(f'[MODULES][{sp}] Модуль с таким именем уже импортирован. Совпадение названия модуля')
                    # quit(code=f'[MODULES][{sp}] Модуль с таким именем уже импортирован. Совпадение названия модуля')

                else:
                    frame_worker(msha256, sp, module_json)

        except FileNotFoundError:
            print(f'[MODULES][{sp}] Ошибка чтения настроек модуля')


if Settings.useModules:
    master_module_integrator()
