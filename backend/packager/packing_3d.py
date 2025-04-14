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
        MIN_DIM = 1
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
                new_length = x3 - x1
                new_width = y2 - y1
                new_height = z2 - z1
                if new_length >= MIN_DIM and new_width >= MIN_DIM and new_height >= MIN_DIM:
                    updatedSpaces.append(Space(Position3(x1, y1, z1), Cube(x3 - x1, y2 - y1, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x1, y1), x3 - x1, y2 - y1))))
            if x2 > x4:
                new_length = x2 - x4
                new_width = y2 - y1
                new_height = z2 - z1
                if new_length >= MIN_DIM and new_width >= MIN_DIM and new_height >= MIN_DIM:
                    updatedSpaces.append(Space(Position3(x4, y1, z1), Cube(x2 - x4, y2 - y1, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x4, y1), x2 - x4, y2 - y1))))
            if y3 > y1:
                new_length = x2 - x1
                new_width = y3 - y1
                new_height = z2 - z1
                if new_length >= MIN_DIM and new_width >= MIN_DIM and new_height >= MIN_DIM:
                    updatedSpaces.append(Space(Position3(x1, y1, z1), Cube(x2 - x1, y3 - y1, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x1, y1), x2 - x1, y3 - y1))))
            if y2 > y4:
                new_length = x2 - x1
                new_width = y2 - y4
                new_height = z2 - z1
                if new_length >= MIN_DIM and new_width >= MIN_DIM and new_height >= MIN_DIM:
                    updatedSpaces.append(Space(Position3(x1, y4, z1), Cube(x2 - x1, y2 - y4, z2 - z1), self.getCrossPlane(space.plane, Plane(Position2(x1, y4), x2 - x1, y2 - y4))))
            if z3 > z1:
                new_length = x2 - x1
                new_width = y2 - y1
                new_height = z3 - z1
                if new_length >= MIN_DIM and new_width >= MIN_DIM and new_height >= MIN_DIM:
                    updatedSpaces.append(Space(Position3(x1, y1, z1), Cube(x2 - x1, y2 - y1, z3 - z1), space.plane))
            if z2 > z4:
                new_length = x2 - x1
                new_width = y2 - y1
                new_height = z2 - z4
                if new_length >= MIN_DIM and new_width >= MIN_DIM and new_height >= MIN_DIM:
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
        max_weight = outer_limit['maxWeight']

        std_blocks = []
        remaining_goods = deepcopy(goods)
        
        WALL = 0.6  # cm
        DENSITY = 0.54  # kg/m²
        def calc_outer_weight(L, W, H):
            area = 2 * (L * W + L * H + W * H) / 10000  # cm² to m²
            return area * DENSITY
    
        # 计算单个标准件加上外壳后的最小重量
        outer_L = std_L + 2 * WALL
        outer_W = std_W + 2 * WALL
        outer_H = std_H + 2 * WALL
        min_shell_weight = calc_outer_weight(outer_L, outer_W, outer_H)
        max_item_weight = max_weight - std_weight - min_shell_weight

        # 每次尝试填满一个标准件
        while any(item.num > 0 for item in remaining_goods.values()):
            self.remainSpace = [Space(
                Position3(0, 0, 0),
                Cube(std_L, std_W, std_H),
                Plane(Position2(0, 0), std_L, std_W)
            )]

            block_contents = []
            current_weight = 0

            while True:
                if not self.remainSpace:
                    break
                space = self.remainSpace[0]
                block_table = self.genSimpleBlock(space, remaining_goods)
                if not block_table:
                    self.remainSpace.pop(0)
                    continue

                best_block = None
                for blk in block_table:
                    block_weight = blk.item.weight * blk.count
                    projected_weight = current_weight + block_weight + std_weight + min_shell_weight
                    if projected_weight <= max_weight:
                        best_block = blk
                        break

                if not best_block:
                    break

                item = remaining_goods[best_block.item.name]
                item.num -= best_block.count
                current_weight += best_block.item.weight * best_block.count

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

        def compute_used_box_dimensions(packed, std_L, std_W, std_H):
            if not packed:
                return 0, 0, 0
            max_x = max(p['position']['x'] + std_L for p in packed)
            max_y = max(p['position']['y'] + std_W for p in packed)
            max_z = max(p['position']['z'] + std_H for p in packed)
            return max_x, max_y, max_z
        
        std_L = std_info['length']
        std_W = std_info['width']
        std_H = std_info['height']

        innerL = maxL - 2 * WALL
        innerW = maxW - 2 * WALL
        innerH = maxH - 2 * WALL

        outer_boxes = []
        queue = deque(std_blocks)
        dims = [('x', std_L), ('y', std_W), ('z', std_H)]
        axis_order = [axis for axis, _ in sorted(dims, key=lambda t: t[1])]
        while queue:
            
            self.remainSpace = [Space(
                Position3(0, 0, 0),
                Cube(innerL, innerW, innerH),
                Plane(Position2(0, 0), innerL, innerW)
            )]

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
                
                self.remainSpace.sort(
                    key=lambda sp: (
                        getattr(sp.position3, axis_order[2]),
                        getattr(sp.position3, axis_order[1]),
                        getattr(sp.position3, axis_order[0])
                    )
                )
                # 在放置前对空间排序，优先填低层空间
                # self.remainSpace.sort(key=lambda sp: (sp.position3.z, sp.position3.x, sp.position3.y))

                pos = None
                for sp in self.remainSpace:
                    pos = self.getPutPosition3(block, sp)
                    if pos is not None:
                        break

                if not pos:
                    temp.append(std)
                    continue

                mock_packed = packed + [{
                    'position': {'x': pos.x, 'y': pos.y, 'z': pos.z}
                }]
                used_L, used_W, used_H = compute_used_box_dimensions(mock_packed, std_L, std_W, std_H)
                predicted_L = min(used_L, innerL)
                predicted_W = min(used_W, innerW)
                predicted_H = min(used_H, innerH)
                predicted_shell_weight = calc_outer_weight(predicted_L + 2 * WALL, predicted_W + 2 * WALL, predicted_H + 2 * WALL)
                predicted_total_weight = gross + weight + predicted_shell_weight

                if predicted_total_weight > maxWeight:
                    temp.append(std)
                    continue

                # 放入箱子
                block.position3 = pos
                self.remainSpace = self.updateSpace(pos, block)
                std['position'] = {
                    "x": pos.x, "y": pos.y, "z": pos.z
                }
                packed.append(std)
                gross += weight

            final_L = min(used_L, innerL)
            final_W = min(used_W, innerW)
            final_H = min(used_H, innerH)
            shell_weight = calc_outer_weight(final_L + 2 * WALL,
                                             final_W + 2 * WALL,
                                             final_H + 2 * WALL)
            used_L, used_W, used_H = compute_used_box_dimensions(packed, std_L, std_W, std_H)
            shell_weight = calc_outer_weight(used_L + 2 * WALL, used_W + 2 * WALL, used_H + 2 * WALL)
            gross += shell_weight

            outer_boxes.append({
                "dimensions": {
                    "length": round(used_L + 2 * WALL, 2),
                    "width": round(used_W + 2 * WALL, 2),
                    "height": round(used_H + 2 * WALL, 2)
                },
                "contents": packed,
                "gross_weight": round(gross, 3)
            })

            queue = temp  # 剩下的标准件进入下一轮

        return outer_boxes
