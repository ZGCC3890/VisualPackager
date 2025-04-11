from copy import deepcopy
import functools

# ---------- 基本结构类 ----------
class Position2:
    def __init__(self, x, y): self.x, self.y = x, y

class Position3:
    def __init__(self, x, y, z): self.x, self.y, self.z = x, y, z

class Plane:
    def __init__(self, pos2, length, width): self.pos2, self.length, self.width = pos2, length, width

class Cube:
    def __init__(self, length, width, height): self.length, self.width, self.height = length, width, height

class Space:
    def __init__(self, pos3, cube, plane): self.position3, self.cube, self.plane = pos3, cube, plane

class Item:
    def __init__(self, name, l, w, h, weight, qty=1):
        self.name = name
        self.length = l
        self.width = w
        self.height = h
        self.weight = weight
        self.num = qty
        self.feasibleDirection = [0]

    def rotateCube(self, direction): return Cube(self.length, self.width, self.height)

class Block:
    def __init__(self):
        self.cube = None
        self.position3 = None
        self.item = None
        self.count = 0

    def getBlockDetail(self, item, direction, i, j, k, tag):
        self.item = item
        self.count = i * j * k
        self.cube = item.rotateCube(direction)

# ---------- 主装箱类 ----------
class Packing3D:
    def __init__(self): self.remainSpace = []

    def isOverlap(self, space1, space2):
        def intersect(a1, a2, b1, b2): return max(a1, b1) < min(a2, b2)
        a, b = space1, space2
        return all([
            intersect(a.position3.x, a.position3.x + a.cube.length, b.position3.x, b.position3.x + b.cube.length),
            intersect(a.position3.y, a.position3.y + a.cube.width, b.position3.y, b.position3.y + b.cube.width),
            intersect(a.position3.z, a.position3.z + a.cube.height, b.position3.z, b.position3.z + b.cube.height)
        ])

    def getCrossPlane(self, a, b): return b

    def spaceCmp1(self, a, b):
        va = a.cube.length * a.cube.width * a.cube.height
        vb = b.cube.length * b.cube.width * b.cube.height
        return -1 if va > vb else (1 if va < vb else 0)

    def blockCmp(self, a, b): return -1 if a.count > b.count else 1

    def getPutPosition3(self, block, space):
        if block.cube.length <= space.cube.length and block.cube.width <= space.cube.width and block.cube.height <= space.cube.height:
            return space.position3
        return None

    def updateSpace(self, position3, block):
        updatedSpaces = []
        for space in self.remainSpace:
            overlap = self.isOverlap(space, Space(position3, block.cube, Plane(Position2(space.position3.x, space.position3.y), block.cube.length, block.cube.width)))
            if not overlap:
                updatedSpaces.append(space)
                continue

            x1, y1, z1 = space.position3.x, space.position3.y, space.position3.z
            x2, y2, z2 = x1 + space.cube.length, y1 + space.cube.width, z1 + space.cube.height
            x3, y3, z3 = max(x1, position3.x), max(y1, position3.y), max(z1, position3.z)
            x4, y4, z4 = min(x2, position3.x + block.cube.length), min(y2, position3.y + block.cube.width), min(z2, position3.z + block.cube.height)

            if x3 > x1:
                updatedSpaces.append(Space(Position3(x1, y1, z1), Cube(x3 - x1, y2 - y1, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x1, y1), x3 - x1, y2 - y1))))
            if x2 > x4:
                updatedSpaces.append(Space(Position3(x4, y1, z1), Cube(x2 - x4, y2 - y1, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x4, y1), x2 - x4, y2 - y1))))
            if y3 > y1:
                updatedSpaces.append(Space(Position3(x1, y1, z1), Cube(x2 - x1, y3 - y1, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x1, y1), x2 - x1, y3 - y1))))
            if y2 > y4:
                updatedSpaces.append(Space(Position3(x1, y4, z1), Cube(x2 - x1, y2 - y4, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x1, y4), x2 - x1, y2 - y4))))
            if z3 > z1:
                updatedSpaces.append(Space(Position3(x1, y1, z1), Cube(x2 - x1, y2 - y1, z3 - z1), space.plane))
            if z2 > z4:
                updatedSpaces.append(Space(Position3(x1, y1, z4), Cube(x2 - x1, y2 - y1, z2 - z4), Plane(Position2(x3, y3), x4 - x3, y4 - y3)))

        updatedSpaces.sort(key=functools.cmp_to_key(self.spaceCmp1))
        return updatedSpaces

    def genSimpleBlock(self, space, items):
        blockTable = []
        L, W, H = space.cube.length, space.cube.width, space.cube.height
        for k in items:
            item = items[k]
            num = item.num
            for direction in item.feasibleDirection:
                cube = item.rotateCube(direction)
                l, w, h = cube.length, cube.width, cube.height
                if l > L or w > W or h > H:
                    continue
                max_i = int(L // l)
                max_j = int(W // w)
                max_k = int(H // h)
                placed = False
                for i in range(min(num, max_i), 0, -1):
                    for j in range(min(num // i, max_j), 0, -1):
                        for k in range(min(num // (i * j), max_k), 0, -1):
                            if i * l > L or j * w > W or k * h > H:
                                continue
                            block = Block()
                            block.getBlockDetail(item, direction, i, j, k, '')
                            pos = self.getPutPosition3(block, space)
                            if pos:
                                block.position3 = deepcopy(pos)
                                blockTable.append(block)
                                placed = True
                                break
                        if placed: break
                    if placed: break
        blockTable.sort(key=functools.cmp_to_key(self.blockCmp))
        return blockTable

    def plan_packing(self, goods, std_info, outer_limit):
        from collections import deque
        from copy import deepcopy

        std_L = std_info['length']
        std_W = std_info['width']
        std_H = std_info['height']
        std_weight = std_info.get('weight', 0)

        std_blocks = []
        remaining_goods = deepcopy(goods)

        # 每次尝试填满一个标准件
        while any(item.num > 0 for item in remaining_goods.values()):
            self.remainSpace = [Space(
                Position3(0, 0, 0),
                Cube(std_L, std_W, std_H),
                Plane(Position2(0, 0), std_L, std_W)
            )]

            block_contents = []

            while True:
                if not self.remainSpace:
                    break
                space = self.remainSpace[0]
                block_table = self.genSimpleBlock(space, remaining_goods)
                if not block_table:
                    self.remainSpace.pop(0)
                    continue

                best_block = block_table[0]
                item = remaining_goods[best_block.item.name]
                item.num -= best_block.count

                block_contents.append({
                    'item': best_block.item.name,
                    'position': {
                        'x': best_block.position3.x,
                        'y': best_block.position3.y,
                        'z': best_block.position3.z
                    },
                    'dimensions': {
                        'length': best_block.cube.length,
                        'width': best_block.cube.width,
                        'height': best_block.cube.height
                    },
                    'quantity': best_block.count,
                    'weight': best_block.item.weight * best_block.count
                })

                self.remainSpace = self.updateSpace(best_block.position3, best_block)

            std_blocks.append({
                'dimensions': {
                    'length': std_L,
                    'width': std_W,
                    'height': std_H
                },
                'contents': block_contents,
                'gross_weight': sum(g['weight'] for g in block_contents) + std_weight
            })

        outer_boxes = self.pack_standard_cases_into_outer_boxes(std_blocks, std_info, outer_limit)
        return { "std_cases": std_blocks, "outer_boxes": outer_boxes }



    def pack_standard_cases_into_outer_boxes(self, std_blocks, std_info, outer_limit):
        from collections import deque

        WALL = 0.6  # cm
        DENSITY = 0.54  # kg/m²

        maxL = outer_limit['maxLength']
        maxW = outer_limit['maxWidth']
        maxH = outer_limit['maxHeight']
        maxWeight = outer_limit['maxWeight']

        def calc_outer_weight(L, W, H):
            area = 2 * (L * W + L * H + W * H) / 10000  # cm² to m²
            return area * DENSITY

        std_L = std_info['length']
        std_W = std_info['width']
        std_H = std_info['height']

        innerL = maxL - 2 * WALL
        innerW = maxW - 2 * WALL
        innerH = maxH - 2 * WALL

        outer_boxes = []
        queue = deque(std_blocks)

        while queue:
            self.remainSpace = [Space(Position3(0, 0, 0),
                                    Cube(innerL, innerW, innerH),
                                    Plane(Position2(0, 0), innerL, innerW))]
            packed = []
            gross = 0
            temp = deque()

            while queue:
                std = queue.popleft()
                if not std['contents']:
                    continue

                block = Block()
                block.cube = Cube(std_L, std_W, std_H)
                weight = std['gross_weight']
                pos = self.getPutPosition3(block, self.remainSpace[0])

                if pos:
                    block.position3 = pos
                    self.remainSpace = self.updateSpace(pos, block)
                    std['position'] = {
                        "x": pos.x, "y": pos.y, "z": pos.z
                    }
                    packed.append(std)
                    gross += weight
                else:
                    temp.append(std)

            usedH = max((s['position']['z'] + std_H for s in packed), default=0)
            gross += calc_outer_weight(innerL, innerW, usedH)

            outer_boxes.append({
                "dimensions": {
                    "length": maxL,
                    "width": maxW,
                    "height": usedH + 2 * WALL
                },
                "contents": packed,
                "gross_weight": gross
            })

            queue = temp

        return outer_boxes

