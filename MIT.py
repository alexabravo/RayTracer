from FuncionesS import *
from FuncionesM import *

class Light(object):
  def __init__(self, color =color(255,255,255),position =V3(0,0,0), intensity = 1):
    self.color = color
    self.position = position
    self.intensity = intensity


class Material(object):
  def __init__(self, diffuse = color(255,255,255), albedo=(1,0,0,0), spec=0, refractive_index=1, texture = None):
    self.diffuse = diffuse
    self.albedo = albedo
    self.spec = spec
    self.refractive_index = refractive_index
    self.texture = texture

class Intersect(object):
  def __init__(self, distance=0, point=None, normal= None, texCoords = None):
    self.distance = distance
    self.point = point
    self.normal = normal
    self.texCoords = texCoords


class Texture(object):
  def __init__(self, path):
    self.path = path
    self.read()

  def read(self):
    image = open(self.path, 'rb')
    image.seek(10)
    headerSize = struct.unpack('=l', image.read(4))[0]

    image.seek(14 + 4)
    self.width = struct.unpack('=l', image.read(4))[0]
    self.height = struct.unpack('=l', image.read(4))[0]
    image.seek(headerSize)

    self.pixels = []

    for y in range(self.height):
      self.pixels.append([])
      for x in range(self.width):
        b = ord(image.read(1)) / 255
        g = ord(image.read(1)) / 255
        r = ord(image.read(1)) / 255
        self.pixels[y].append(color(r, g, b))

    image.close()

  def getColor(self, tx, ty):
    if tx >= 0 and tx <= 1 and ty >= 0 and ty <= 1:
      x = int(tx * self.width)
      y = int(ty * self.height)
      return self.pixels[y][x]
    else:
      return color(0, 0, 0)
