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

def readSeriesLogoImages(seriesId):

    imagePath = Path().absolute().parent / 'resources' / 'images' / 'series'
    imageNameWithFileFormat = f"{seriesId}.png"
    imagePath = str(imagePath / imageNameWithFileFormat)
    try:
        return plt.imread(imagePath)
    except FileNotFoundError:
        print(f"Image not found: {imagePath}")
    except Exception as e:
        print(f"Error loading image: {imagePath}, {e}")

def readTrackImages(trackId):

    imagePath = Path().absolute().parent / 'resources' / 'images' / 'tracks'
    imageNameWithFileFormat = f"{trackId}.png"
    imagePath = str(imagePath / imageNameWithFileFormat)
    try:
        return plt.imread(imagePath)
    except FileNotFoundError:
        print(f"Image not found: {imagePath}")
    except Exception as e:
        print(f"Error loading image: {imagePath}, {e}")

def identImageName(id):

    manufacturer_map = {
        43: "mclaren", 71: "mclaren", 188: "mclaren", 135: "mclaren",
        55: "bmw", 159: "bmw", 122: "bmw", 132: "bmw", 189: "bmw",
        88: "porsche", 100: "porsche", 102: "porsche", 119: "porsche",
        137: "porsche", 143: "porsche", 169: "porsche", 174: "porsche",
        72: "merc", 156: "merc", 157: "merc", 161: "merc", 145: "merc",
        65: "aston", 150: "aston",
        147: "honda",
        56: "toyota", 62: "toyota", 69: "toyota", 116: "toyota",
        141: "toyota", 152: "toyota", 155: "toyota", 160: "toyota",
        146: "hyundai", 153: "hyundai",
        28: "ford", 30: "ford", 40: "ford", 46: "ford", 51: "ford",
        59: "ford", 61: "ford", 81: "ford", 92: "ford", 110: "ford",
        115: "ford", 118: "ford", 123: "ford", 125: "ford", 140: "ford", 185: "ford",
        27: "vw", 91: "vw", 138: "vw",
        29: "dallara", 57: "dallara", 99: "dallara", 106: "dallara",
        128: "dallara", 129: "dallara",
        12: "chevrolet", 20: "chevrolet", 22: "chevrolet", 24: "chevrolet",
        26: "chevrolet", 38: "chevrolet", 45: "chevrolet", 58: "chevrolet",
        63: "chevrolet", 70: "chevrolet", 103: "chevrolet", 111: "chevrolet",
        114: "chevrolet", 124: "chevrolet", 127: "chevrolet", 139: "chevrolet",
        151: "chevrolet", 167: "chevrolet", 184: "chevrolet",
        73: "audi", 76: "audi", 98: "audi", 112: "audi", 176: "audi",
        48: "ruf", 49: "ruf", 50: "ruf", 52: "ruf",
        1: "skipbarber",
        60: "holden", 117: "holden",
        3: "pontiac", 10: "pontiac", 175: "pontiac",
        101: "subaru",
        5: "uslegends", 11: "uslegends", 82: "uslegends",
        25: "lotusclassic", 42: "lotusclassic",
        78: "dirtcarracing", 79: "dirtcarracing", 80: "dirtcarracing",
        83: "dirtcarracing", 85: "dirtcarracing", 95: "dirtcarracing",
        131: "superdirtcar", 134: "superdirtcar",
        171: "superformula", 172: "superformula",
        89: "usacracing",
        154: "buick",
        104: "offroadracingseries", 107: "offroadracingseries", 113: "offroadracingseries",
        77: "nissan",
        142: "vee",
        149: "radical", 13: "radical",
        41: "cadillac", #others?
        4: "promazda",
        74: "fr20",
        105: "fr35",
        178: "superformulalights",
        164: "solidrockcarriers",
        67: "mazda", 34: "mazda", 35: "mazda",
        162: "renault",
        2: "empty", 31: "empty", 37: "empty", 54: "empty", 148: "empty"
    }

    return manufacturer_map.get(id, str(id))
