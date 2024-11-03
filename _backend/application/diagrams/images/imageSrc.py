from matplotlib import pyplot as plt


def readImagesForCarId(carIds):
    imgs = []
    for id in carIds:

        imageSrc = findImageSrc(id)

        imagePath = f"../application/diagrams/images/cars/{imageSrc}.png"
        try:
            img = plt.imread(imagePath)
            imgs.append(img)
        except FileNotFoundError:
            print(f"Image not found: {imagePath}")
        except Exception as e:
            print(f"Error loading image: {imagePath}, {e}")
    return imgs

def findImageSrc(id):
    # id = 171
    mcl = [43, 71, 188, 135]
    bmw = [55, 159, 122, 132, 189]
    porsche = [88, 100, 102, 119, 137, 143, 169, 174]
    merc = [72, 156, 157, 161, 145]
    aston = [65, 150]
    honda = [147]
    toyota = [56, 62, 69, 116, 141, 152, 155, 160]
    hyundai = [146, 153]
    ford = [28, 30, 40, 46, 51, 59, 61, 81, 92, 110, 115, 118, 123, 125, 140, 185]
    vw = [27, 91, 138]
    dallara = [29, 57, 99, 106, 128, 129]
    chevrolet = [12, 20, 22, 24, 26, 38, 45, 58, 63, 70, 103, 111, 114, 124, 127, 139, 151, 167, 184]
    _nan = [2, 31, 37, 54, 148]
    audi = [73, 76, 98, 112, 176]
    ruf = [48, 49, 50, 52]
    skipbarber = [1]
    holden = [60, 117]
    pontiac = [3, 10, 175]
    subaru = [101]
    uslegends = [5, 11, 82]
    lotusClassic = [25, 42]
    dirtcarRacing = [78, 79, 80, 83, 85, 95]
    superDirtcar = [131, 134]
    superFormula = [171, 172]
    usacRacing = [67, 89]
    buick = [154]
    offroadRacingSeries = [104, 107, 113]


    if id in mcl:
        return "mclaren"
    elif id in bmw:
        return "bmw"
    elif id in porsche:
        return "porsche"
    elif id in merc:
        return "merc"
    elif id in aston:
        return "aston"
    elif id in toyota:
        return "toyota"
    elif id in honda:
        return "honda"
    elif id in hyundai:
        return "hyundai"
    elif id in ford:
        return "ford"
    elif id in vw:
        return "vw"
    elif id in dallara:
        return "dallara"
    elif id in chevrolet:
        return "chevrolet"
    elif id in audi:
        return "audi"
    elif id in ruf:
        return "ruf"
    elif id in skipbarber:
        return "skipbarber"
    elif id in holden:
        return "holden"
    elif id in pontiac:
        return "pontiac"
    elif id in subaru:
        return "subaru"
    elif id in buick:
        return "buick"
    elif id in uslegends:
        return "uslegends"
    elif id in lotusClassic:
        return "lotusclassic"
    elif id in dirtcarRacing:
        return "dirtcarracing"
    elif id in superDirtcar:
        return "superdirtcar"
    elif id in offroadRacingSeries:
        return "offroadracingseries"
    elif id in usacRacing:
        return "usacracing"
    elif id in superFormula:
        return "superformula"
    elif id in _nan:
        return "empty"