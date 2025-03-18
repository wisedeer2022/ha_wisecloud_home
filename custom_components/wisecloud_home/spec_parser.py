import json


async def parse(spec: dict):
    props = spec["properties"]
    switchs = []
    strings = []
    numbers = []
    selects = []
    sensors = []
    events = event_parse(spec["events"])
    for prop in props:
        data_type = prop["define"]["type"]

        if prop["mode"] == "rw" and data_type == "bool":
            switchs.append(prop)
        elif prop["mode"] == "rw" and data_type == "string":
            strings.append(prop)
        elif prop["mode"] == "rw" and data_type == "int":
            numbers.append(prop)
        elif prop["mode"] == "rw" and data_type == "enum":
            selects.append(prop)
        elif prop["mode"] == "r" and data_type == "int":
            sensors.append(prop)
    return switchs, strings, numbers, selects, sensors, events


def event_parse(events) :
    datas = []
    # 遍历每个事件
    for event in events:
        data = {
            "id": event["id"],
            "name": event["name"],
        }

        if event["id"] == "lock_event":
            # 遍历该事件的每个参数
            for param in event["params"]:
                if param["id"] == "lock_action":
                    # 获取 mapping 信息
                    mapping = param["define"]["mapping"]
                    data["mapping"] = mapping
                    datas.append(data)
                    break
        elif event["id"] == "camera_event":
            # 遍历该事件的每个参数
            for param in event["params"]:
                if param["id"] == "event_type":
                    # 获取 mapping 信息
                    mapping = param["define"]["mapping"]
                    data["mapping"] = mapping
                    datas.append(data)
                    break
        elif event["id"] == "lock_exception":
            # 遍历该事件的每个参数
            for param in event["params"]:
                if param["id"] == "abnormal_condition":
                    # 获取 mapping 信息
                    mapping = param["define"]["mapping"]
                    data["mapping"] = mapping
                    datas.append(data)
                    break
        elif event["id"] == "power_supply_event":
            # 遍历该事件的每个参数
            for param in event["params"]:
                if param["id"] == "power_supply_mode":
                    # 获取 mapping 信息
                    mapping = param["define"]["mapping"]
                    data["mapping"] = mapping
                    datas.append(data)
                    break
        else: continue

    return datas
