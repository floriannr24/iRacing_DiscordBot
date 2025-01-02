from pathlib import Path

from matplotlib import pyplot as plt


def readCarLogoImages(carIds):
    imgs = []
    for id in carIds:

        imagePath = Path().absolute().parent / 'resources' / 'images' / 'cars'
        imageName = str(identImageName(id))
        imageNameWithFileFormat = f"{imageName}.png"
        imagePath = str(imagePath / imageNameWithFileFormat)
        try:
            img = plt.imread(imagePath)
            imgs.append(img)
        except FileNotFoundError:
            print(f"Image not found: {imagePath}")
        except Exception as e:
            print(f"Error loading image: {imagePath}, {e}")
    return imgs

def readSeriesLogoImage(seriesId):

    imagePath = Path().absolute().parent / 'resources' / 'images' / 'series'
    imageNameWithFileFormat = f"{seriesId}.png"
    imagePath = str(imagePath / imageNameWithFileFormat)
    try:
        return plt.imread(imagePath)
    except FileNotFoundError:
        print(f"Image not found: {imagePath}")
    except Exception as e:
        print(f"Error loading image: {imagePath}, {e}")

def readWeatherImage(rainState):
    imagePath = Path().absolute().parent / 'resources' / 'images' / 'weather'
    imageNameWithFileFormat = f"{rainState}.png"
    imagePath = str(imagePath / imageNameWithFileFormat)
    try:
        return plt.imread(imagePath)
    except FileNotFoundError:
        print(f"Image not found: {imagePath}")
    except Exception as e:
        print(f"Error loading image: {imagePath}, {e}")


def identImageName(id):

    manufacturer_map = {
        1: "skipbarber",
        2: "empty",
        3: "pontiac",
        4: "promazda",
        5: "uslegends",
        10: "pontiac",
        11: "uslegends",
        12: "chevrolet",
        13: "radical",
        20: "chevrolet",
        22: "chevrolet",
        24: "chevrolet",
        25: "lotusclassic",
        26: "chevrolet",
        27: "vw",
        28: "ford",
        29: "dallara",
        30: "ford",
        31: "empty",
        34: "mazda",
        35: "mazda",
        37: "empty",
        38: "chevrolet",
        40: "ford",
        41: "cadillac",
        42: "lotusclassic",
        43: "mclaren",
        45: "chevrolet",
        46: "ford",
        48: "ruf",
        49: "ruf",
        50: "ruf",
        51: "ford",
        52: "ruf",
        54: "empty",
        55: "bmw",
        56: "toyota",
        57: "dallara",
        58: "chevrolet",
        59: "ford",
        60: "holden",
        61: "ford",
        62: "toyota",
        63: "chevrolet",
        65: "aston",
        67: "mazda",
        69: "toyota",
        70: "chevrolet",
        71: "mclaren",
        72: "merc",
        73: "audi",
        74: "fr20",
        76: "audi",
        77: "nissan",
        78: "dirtcarracing",
        79: "dirtcarracing",
        80: "dirtcarracing",
        81: "ford",
        82: "uslegends",
        83: "dirtcarracing",
        85: "dirtcarracing",
        88: "porsche",
        89: "usacracing",
        91: "vw",
        92: "ford",
        95: "dirtcarracing",
        98: "audi",
        99: "dallara",
        100: "porsche",
        101: "subaru",
        102: "porsche",
        103: "chevrolet",
        104: "offroadracingseries",
        105: "fr35",
        106: "dallara",
        107: "offroadracingseries",
        110: "ford",
        111: "chevrolet",
        112: "audi",
        113: "offroadracingseries",
        114: "chevrolet",
        115: "ford",
        116: "toyota",
        117: "holden",
        118: "ford",
        119: "porsche",
        122: "bmw",
        123: "ford",
        124: "chevrolet",
        125: "ford",
        127: "chevrolet",
        128: "dallara",
        129: "dallara",
        131: "superdirtcar",
        132: "bmw",
        134: "superdirtcar",
        135: "mclaren",
        137: "porsche",
        138: "vw",
        139: "chevrolet",
        140: "ford",
        141: "toyota",
        142: "vee",
        143: "porsche",
        144: "ferrari",
        145: "merc",
        146: "hyundai",
        147: "honda",
        148: "empty",
        149: "radical",
        150: "aston",
        151: "chevrolet",
        152: "toyota",
        153: "hyundai",
        154: "buick",
        155: "toyota",
        156: "merc",
        157: "merc",
        158: "porsche",
        159: "bmw",
        160: "toyota",
        161: "merc",
        162: "renault",
        164: "solidrockcarriers",
        167: "chevrolet",
        168: "cadillac",
        169: "porsche",
        171: "superformula",
        172: "superformula",
        173: "ferrari",
        174: "porsche",
        175: "pontiac",
        176: "audi",
        178: "superformulalights",
        184: "chevrolet",
        185: "ford",
        188: "mclaren",
        189: "bmw",
        190: "ford",
        192: "chevrolet",
        194: "acura",
        195: "bmw",
        196: "ferrari"
    }

    return manufacturer_map.get(id, str(id))
