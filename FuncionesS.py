import struct

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(c):
    return struct.pack('=h', c)

def dword(c):
    return struct.pack('=l', c)

#def color(r, g, b):
     #return bytes([b, g, r])

#def color2(r, g, b):
  #return bytes([b, g, r])

class color(object):
  def __init__(self,r,g,b):
    self.r = r
    self.g = g
    self.b = b

  def __add__(self, other_color):
    r = self.r + other_color.r
    g = self.g + other_color.g
    b = self.b + other_color.b

    return color(r,g,b)

  def __mul__(self, other):
    r = self.r * other
    g = self.g * other
    b = self.b * other

    return color(r,g,b)
  __rmul__ = __mul__

  def __repr__(self):
    return "color(%s, %s, %s)" % (self.r, self.g,self.b)

  def toBytes(self):
    self.r = int(max(min(self.r, 255), 0))
    self.g = int(max(min(self.g, 255), 0))
    self.b = int(max(min(self.b, 255), 0))
    return bytes([self.b,self.g,self.r])
