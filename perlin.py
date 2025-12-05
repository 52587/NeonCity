import random
import math

# Permutation table
PERMUTATION = [151,160,137,91,90,15,
131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180] * 2

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(t, a, b):
    return a + t * (b - a)

def grad(hash, x):
    h = hash & 15
    grad = 1 + (h & 7) # Gradient value 1-8
    if (h & 8): grad = -grad # Randomly invert
    return (grad * x) 

def grad2(hash, x, y):
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h == 12 or h == 14 else 0)
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

def noise2(x, y):
    X = int(math.floor(x)) & 255
    Y = int(math.floor(y)) & 255
    x -= math.floor(x)
    y -= math.floor(y)
    u = fade(x)
    v = fade(y)
    A = PERMUTATION[X] + Y
    AA = PERMUTATION[A]
    AB = PERMUTATION[A+1]
    B = PERMUTATION[X+1] + Y
    BA = PERMUTATION[B]
    BB = PERMUTATION[B+1]
    return lerp(v, lerp(u, grad2(PERMUTATION[AA], x, y), grad2(PERMUTATION[BA], x-1, y)),
                   lerp(u, grad2(PERMUTATION[AB], x, y-1), grad2(PERMUTATION[BB], x-1, y-1)))

def pnoise2(x, y, octaves=1, persistence=0.5, lacunarity=2.0, repeat=1024, base=0):
    total = 0
    frequency = 1
    amplitude = 1
    max_value = 0
    for _ in range(octaves):
        total += noise2(x * frequency + base, y * frequency + base) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return total / max_value

def noise1(x):
    # Find unit grid cell containing point
    X = int(math.floor(x)) & 255
    # Relative x of point in cell
    x -= math.floor(x)
    
    # Compute fade curves for x
    u = fade(x)
    
    # Hash coordinates of the 2 corners
    A = PERMUTATION[X]
    B = PERMUTATION[X+1]
    
    # Add blended results from 2 corners
    return lerp(u, grad(A, x), grad(B, x-1))

def pnoise1(x, octaves=1, persistence=0.5, lacunarity=2.0, repeat=1024, base=0):
    total = 0
    frequency = 1
    amplitude = 1
    max_value = 0  # Used for normalizing result to 0.0 - 1.0
    
    for _ in range(octaves):
        total += noise1(x * frequency + base) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    
    return total / max_value
