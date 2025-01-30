import math
from tiles  import generateLevels
width = 50000
height = 40000

smaller_scales = [
16,
8,
4,
2,
1
]

base_size = (3125,2500)


smaller_widths = []
smaller_sizes = []
smaller_scales_sq = []
add_colors = []

 
for value in smaller_scales:
        smaller_widths.append(math.floor( width / (value)))
        smaller_sizes.append((math.floor(width / (value)),math.floor(height / (value))) )
        sq = value*value
        smaller_scales_sq.append(sq)
        add_colors.append(1.0/float(sq))






