from PIL import Image
import os
import math


def create_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


class Tile:

    def __init__(self,
                 path,  onload,
                 mode: str,
                 size: tuple[int, int] | list[int],
                 color: float | tuple[float, ...] | str | None = 0
                 ):

        self.mode = mode
        self.color = color
        self.path = path
        self.size = size
        self.tile = None
        self.onload = onload

    def load(self):
        self.onload()
        # print(f"loading {self.path}")
        if os.path.exists(self.path):
            imagef = Image.open(self.path)
            self.tile = imagef
        else:
            self.tile = Image.new(self.mode, self.size, color=self.color)

    def offload(self):
        # print(f"offload {self.path}")
        create_dir(self.path)
        if self.tile is not None:
            self.tile.save(self.path)
        self.tile = None

    def putpixel(self, xy, color):
        if self.tile is None:
            self.load()
        self.tile.putpixel(xy, color)

    def getpixel(self, xy):
        if self.tile is None:
            self.load()
        return self.tile.getpixel(xy)

    def paste(self,
              im: Image,
              box: tuple[int, int],
              mask: None = None
              ):
        if self.tile is None:
            self.load()
        self.tile.paste(im, box, mask)


class ImageTileGen:
    def __init__(self,
                 output_directory: str,
                 tile_size: tuple[int, int],
                 max_load: int,
                 mode: str,
                 size: tuple[int, int] | list[int],
                 color: float | tuple[float, ...] | str | None = 0,
                 ):

        self.mode = mode
        self.color = color
        self.max_load = max_load
        self.size = size
        self.output_directory = output_directory
        self.width = self.size[0]
        self.height = self.size[1]
        self.tile_size = tile_size
        self.tiles = []
        self.saved_tiles = []
        self.rows = None
        self._create_tiles()

    def _create_tiles(self):
        width, height = self.size
        x_tiles = width // self.tile_size[0] + \
            (1 if width % self.tile_size[0] else 0)
        y_tiles = height // self.tile_size[1] + \
            (1 if height % self.tile_size[1] else 0)
        self.rows = x_tiles

        i = 0

        for y in range(y_tiles):
            for x in range(x_tiles):
                left = x * self.tile_size[0]
                upper = y * self.tile_size[1]
                tile_width = min(self.tile_size[0], width - left)
                tile_height = min(self.tile_size[1], height - upper)

                tile = Tile(os.path.join(self.output_directory, f"tile_{i}.png"),
                            self.regulate,  self.mode,  (tile_width, tile_height), self.color)
                # tile = Image.new('RGB', (tile_width, tile_height), color='black')
                self.tiles.append(tile)
                i += 1

    def regulate(self):
        g = self.get_offloads()
        if (g > self.max_load):
            # print(f"Offloads exceeded {g}")
            self.offload_current()

    def get_offloads(self):
        return sum(1 for item in self.tiles if item.tile is not None)

    def offload_current(self):
        for x in self.tiles:
            if (x.tile is not None):
                x.offload()

    def global_zero(self, globaL):
        x, y = globaL

        tile_x = x // self.tile_size[0]
        tile_y = y // self.tile_size[1]
        tile_index = tile_y * (self.size[0] // self.tile_size[0] + 1) + tile_x
        local_x = x % self.tile_size[0]
        local_y = y % self.tile_size[1]
        return (tile_index, local_x, local_y)

    def global_local(self, globaL):
        x, y = globaL

        tile_x = x // self.tile_size[0]
        tile_y = y // self.tile_size[1]
        # rows =self.size[0] // self.tile_size[0]
        tile_index = tile_y * (self.rows) + tile_x
        local_x = x % self.tile_size[0]
        local_y = y % self.tile_size[1]

        return (tile_index, local_x, local_y)

    def putpixel(self, globaL, color):
        tile_index, local_x, local_y = self.global_local(globaL)
        # if tile_index < len(self.tiles):
        tile = self.tiles[tile_index]
        #     if local_x < tile.size[0] and local_y < tile.size[1]:
        tile.putpixel((local_x, local_y), color)

    def getpixel(self, globaL):
        tile_index, local_x, local_y = self.global_local(globaL)
        # if tile_index < len(self.tiles):
        tile = self.tiles[tile_index]
        #     if local_x < tile.size[0] and local_y < tile.size[1]:
        return tile.getpixel((local_x, local_y))
        # return None  # Return None if the coordinates are out of bounds

    def save(self):
        for i, tile in enumerate(self.tiles):
            tile.offload()
            # tile.save(f"{output_directory}/{prefix}_{i}.png")


def generateLevels(path, tile_size, smaller_sizes, level, x, y):

    levelindex = len(smaller_sizes) - level
    levelsize = smaller_sizes[levelindex - 1]
    levelwidth = levelsize[0]
    levelheight = levelsize[1]
    groupdir = None

    if (level == 0):
        groupdir = path
    else:
        groupdir = os.path.join(path, f"{levelwidth}x{levelheight}")

    tiles = ImageTileGen(groupdir, tile_size, 50, "1",
                       (levelwidth, levelheight), 0)

    local = tiles.global_local((x, y))
    if (local[0] > len(tiles.tiles)):
        return None

    tile = tiles.tiles[local[0]]
    filename = tile.path 

    if (os.path.exists(filename)):
        return tile
    else:
        if (level == 0):
            return None

        scaledx = x * 2
        scaledy = y * 2

        tilex = tile_size[0]
        tiley = tile_size[1]
        halfx = math.floor(tilex / 2)
        halfy = math.floor(tiley / 2)

        listxy = [
            (scaledx,       scaledy,       0,           0),
            (scaledx+tilex, scaledy,       halfx,       0),
            (scaledx,       scaledy+tiley, 0,       halfy),
            (scaledx+tilex, scaledy+tiley, halfx,   halfy),
        ]

        for xy in listxy:
            x, y, hx, hy = xy
            lowertile = generateLevels(
                path, tile_size, smaller_sizes, level - 1, x, y)

            if (lowertile == None):
                continue

            print(lowertile.path)
            lowertile.load()
            img = lowertile.tile

            resized = img.resize((halfx, halfy), Image.BILINEAR)

            tile.paste(resized, (hx, hy))

        tile.offload()

        return tile



def recursive_tile_index(s):
    s = str(s)
    length = len(s)
    digits = [int(c) for c in s[1:]]
    index = 0

    if length == 0:
        return 0
    elif length == 1:
        return int(s[0])
    elif length == 2:
        return int(s[1])
    elif length == 3:
        c, d = digits
        if c >= 2:
            index += 8 + (c - 2) * 1 
        else:
            index += c * 2
        if d >= 2:
            index += 4 + (d - 2) * 1 
        else:
            index += d
        if c == 3:
            index += 1  # ?
    elif length == 4:
        b, c, d = digits
        if b >= 2:
            index += 32 + (b - 2) * 4  # base = 32
        else:
            index += b * 4
        if c >= 2:
            index += 16 + (c - 2) * 2 
        else:
            index += c * 2
        if d >= 2:
            index += 8 + (d - 2) * 1  
        else:
            index += d
    elif length == 5:
        b, c, d, e = digits
        if b >= 2:
            index += 128 + (b - 2) * 8  # base = 128
        else:
            index += b * 8
        if c >= 2:
            index += 64 + (c - 2) * 4 
        else:
            index += c * 4
        if d >= 2:
            index += 32 + (d - 2) * 2  
        else:
            index += d * 2
        if e >= 2:
            index += 16 + (e - 2) * 1 
        else:
            index += e
    else:
        return 0

    return index
