import struct
import math
from envmap import *
from Figuras import *
from FuncionesM import *
from MIT import *

MAX_RECURSION_DEPTH = 3

class RayTracer(object):
    
    def __init__(self, filename):
      self.scene = []
      self.width = 0
      self.height = 0
      self.xVP = 0
      self.yVP = 0
      self.wVP = 0
      self.hVP = 0
      self.glClear()
      self.activeT = None
      self.light = None
      self.clear_color = color(0, 51, 102)
      self.framebuffer = []
      self.filename = filename
      self.envmap = None
      
    def glClear(self):
      self.framebuffer = [[self.clear_color for x in range(self.width)] for y in range(self.height)]
      self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    def glpoint(self, x, y):
      self.framebuffer[y][x] = self.clear_color

    def glCreateWindow(self, width, height):
      self.width = width
      self.height = height

    def glClearColor(self, red, blue, green):
      self.clear_color = color(red, blue, green)

    def glViewPort(self, x, y, wVP, hVP):
        self.xVP = x
        self.yVP = y
        self.wVP = wVP
        self.hVP = hVP

    def glVertex(self, x, y):
        x_Ver = int(round(self.wVP/2)*(x+1))
        y_Ver = int(round(self.yVP/2)*(x+1))
        x_pnt = self.xVP + x_Ver
        y_pnt = self.yVP + y_Ver
        self.glpoint((x_pnt),(y_pnt))

    def glLine(self, x1, y1, x2, y2):
      dy = abs(y2 - y1)
      dx = abs(x2 - x1)
      steep = dy > dx

      if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)

      if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

      offset = 0
      threshold = 1
      y = y1
      for x in range(x1, x2):
        if steep:
          self.glpoint(y, x)
        else:
          self.glpoint(x, y)

        offset += dy * 2

        if offset >= threshold:
          y += 1 if y1 < y2 else -1
          threshold += 2 * dx

    def writebmp(self):
        
      f = open(self.filename, 'bw')
      f.write(char('B'))
      f.write(char('M'))
      f.write(dword(14 + 40 + self.width * self.height * 3))
      f.write(dword(0))
      f.write(dword(14 + 40))

      f.write(dword(40))
      f.write(dword(self.width))
      f.write(dword(self.height))
      f.write(word(1))
      f.write(word(24))
      f.write(dword(0))
      f.write(dword(self.width * self.height * 3))
      f.write(dword(0))
      f.write(dword(0))
      f.write(dword(0))
      f.write(dword(0))

      for x in range(self.height):
        for y in range(self.width):
          f.write(self.framebuffer[x][y].toBytes())
      f.close()

    def glFinish(self):
      self.writebmp()

    def cast_ray(self, orig, direction, recursion=0):
      material, impact = self.scene_intersect(orig, direction)

      if material is None or recursion >= MAX_RECURSION_DEPTH:
        if self.envmap:
          return self.envmap.get_color(direction)

        return self.clear_color




      offset_normal = mul(impact.normal, 1.1)

      if material.albedo[2] > 0:
        reverse_direction = mul(direction, -1)
        reflected_dir = reflect(reverse_direction, impact.normal)
        reflect_orig = sub(impact.point, offset_normal) if dot(reflected_dir, impact.normal) < 0 else sum(
          impact.point, offset_normal)
        reflected_color = self.cast_ray(reflect_orig, reflected_dir, recursion + 1)
      else:
        reflected_color = color(0, 0, 0)

      if material.albedo[3] > 0:
        refract_dir = refract(direction, impact.normal, material.refractive_index)
        refract_orig = sub(impact.point, offset_normal) if dot(refract_dir, impact.normal) < 0 else sum(
          impact.point, offset_normal)
        refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
      else:
        refract_color = color(0, 0, 0)

      light_dir = norm(sub(self.light.position, impact.point))
      light_distance = length(sub(self.light.position, impact.point))

      shadow_orig = sub(impact.point, offset_normal) if dot(light_dir, impact.normal) < 0 else sum(
        impact.point, offset_normal)
      shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
      shadow_intensity = 0

      if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
        shadow_intensity = 0.9

      intensity = self.light.intensity * max(0, dot(light_dir, impact.normal)) * (1 - shadow_intensity)

      reflection = reflect(light_dir, impact.normal)
      specular_intensity = self.light.intensity * (
              max(0, -dot(reflection, direction)) ** material.spec
      )

      diffuse = material.diffuse * intensity * material.albedo[0]
      specular = color(255, 255, 255) * specular_intensity * material.albedo[1]
      reflection = reflected_color * material.albedo[2]
      refraction = refract_color * material.albedo[3]


      if material.texture and impact.texCoords is not None:
        text_color = material.texture.getColor(impact.texCoords[0], impact.texCoords[1])
        diffuse = text_color * 255

      return diffuse + specular + reflection + refraction

    def scene_intersect(self, orig, dir):
      zbuffer = float('inf')
      material = None
      intersect = None

      for obj in self.scene:
        hit = obj.ray_intersect(orig, dir)
        if hit is not None:
          if hit.distance < zbuffer:
            zbuffer = hit.distance
            material = obj.material
            intersect = hit

      return material, intersect


    def render(self):
      fun = int(math.pi / 2)
      for y in range(self.height):
        for x in range(self.width):
          i = (2 * (x + 0.5) / self.width - 1) * math.tan(fun / 2) * self.width / self.height
          j = (2 * (y + 0.5) / self.height - 1) * math.tan(fun / 2)
          direction = norm(V3(i, j, -1))
          self.framebuffer[y][x] = self.cast_ray(V3(0, 0, 0), direction)

nube = Material(diffuse=color(255,255,255), albedo=(1, 0, 0, 0, 0),spec=0)
verde = Material(diffuse=color(51,255,51), albedo=(1, 0.5, 0, 0, 0),spec=50)
sol = Material(diffuse=color(250, 253, 15), albedo=(1, 0, 0, 0), spec=0)
negro = Material(diffuse=color(191,189,190), albedo=(0.9, 0.1, 0, 0, 0), spec=10)
cabeza = Material(texture=Texture('./Texturas/perrito.bmp'))
volcan = Material(diffuse=color(102,51, 0), albedo=(0.5, 0.1, 0, 0, 0), spec=10)  
grama = Material(texture=Texture('./Texturas/g.bmp'))
glass = Material(diffuse=color(150, 180, 200), albedo=(0, 0.5, 0.1, 0.8), spec=125, refractive_index=1.5)
water = water = Material(diffuse=color(170,224,241), albedo=(0.2, 0.3, 0.8, 0), spec=60, refractive_index=1.5)

r = RayTracer("Prueba.bmp")
r.glCreateWindow(500,400)
r.glClear()
r.envmap = Envmap('./Texturas/cielo.bmp')

r.light = Light(
  position=V3(-20, 20, 20),
  intensity=1.5
)
r.scene = [
##Nube    
Cube(V3(-3.25, 2.5, -14), 1.25, nube),
Cube(V3(-5.5, 2.5, -14), 1.25, nube),
Cube(V3(-3.75, 3.5, -12.5), 1.25, nube),
Cube(V3(-5, 3.5, -12.5), 1.25, nube),
Cube(V3(-2.5, 3.5, -12.5), 1.25, nube),
Cube(V3(-2.5, 4.5, -13), 1.25, nube),

##Perrito
Cube(V3(3.5, -0.15, -11), 1, cabeza),
Cube(V3(3.5, -0.85, -11), 0.75, negro),
Cube(V3(3.5, -1.55, -11), 0.75, negro),
Cube(V3(3.5, -2.25, -11), 0.75, negro),
Cube(V3(3.85, -2.25, -10), 0.375, negro),
Cube(V3(3.85, -2.5, -10), 0.375, negro),
Cube(V3(3.65, -2.25, -10), 0.375, negro),
Cube(V3(3.65, -2.5, -10), 0.375, negro),
Cube(V3(3, -2.25, -10), 0.375, negro),
Cube(V3(3, -2.5, -10), 0.375, negro),
Cube(V3(2.75, -2.25, -10), 0.375, negro),
Cube(V3(2.75, -2.5, -10), 0.375, negro),

##Volcan 
Pyramid([V3(2, 0, -10), V3(0, 3, -10), V3(-2, 0, -10), V3(2, 0, -10)], volcan),

##Burbujas
Sphere(V3(2.25, 1.5, -8), 0.75, glass),
Sphere(V3(-3.75, 0.25, -8), 0.35, water),

##Campo
Plane(V3(-5, -1.5, -10), V3(0, 1, 0.05), verde),

##Sol
Sphere(V3(1.5, 3.5, -8), 0.5, sol)
]
r.render()
r.glFinish()
