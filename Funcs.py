import os
import numpy as np
from stl import mesh

import Texts


def evaluate_price(model_downloaded_file, material):
    __create_temp_file__(data=model_downloaded_file)
    volume = get_stl_volume('temp_model.stl')
    __remove_temp_file__()
    # TODO: ФОРМУЛА = ОБЪЁМ/1000 * 1.3 * ЦЕНА МАТЕРИАЛА/1000 * 10
    material_price = Texts.materials_price_dict()[material]
    price = volume/1000 * 1.3 * material_price/1000 * 10
    price = max(price, 1000)
    return int(price)


def get_stl_volume(file_path):
    try:
        file_mesh = mesh.Mesh.from_file(file_path)
        volume, cog, inertia = file_mesh.get_mass_properties()
        return volume
    except Exception: return -1


def __create_temp_file__(data):
    with open('temp_model.stl', 'wb') as new_file:
        new_file.write(data)


def __remove_temp_file__():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp_model.stl')
    os.remove(path)






