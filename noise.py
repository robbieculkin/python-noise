#!/usr/bin/env python

import random, math, Image

def lerp(x, y, a):
    return x * (1 - a) + y * a

"""
Texture generation using Perlin noise
"""
class NoiseUtils:
    
    def __init__(self, imageSize):
        self.imageSize = imageSize
        self.gradientNumber = 256

        self.grid = [[]]
        self.gradients = []
        self.values = []
        self.permutations = []
        self.img = {}

        self.__generateGradientVectors()
        self.__normalizeGradientVectors()
        self.__generatePermutationsTable()

    def __generateGradientVectors(self):
        for i in range(self.gradientNumber):
            while True:
                x, y = random.uniform(-1, 1), random.uniform(-1, 1)
                if x * x + y * y < 1:
                    self.gradients.append([x, y])
                    break

        for j in range(self.gradientNumber):
            self.values.append(random.randint(0, 255))

    def __normalizeGradientVectors(self):
        for i in range(self.gradientNumber):
            x, y = self.gradients[i][0], self.gradients[i][1]
            length = math.sqrt(x * x + y * y)
            self.gradients[i] = [x / length, y / length]

    # The modern version of the Fisher-Yates shuffle
    def __generatePermutationsTable(self):
        self.permutations = [i for i in range(self.gradientNumber)]
        for i in reversed(range(self.gradientNumber)):
            j = random.randint(0, i)
            self.permutations[i], self.permutations[j] = \
                self.permutations[j], self.permutations[i]

    def getHashedIndex(self, x, y):
        return (x + self.permutations[y % self.gradientNumber]) % self.gradientNumber

    def valueNoise(self, x, y):
        qx0 = int(math.floor(x))
        qx1 = qx0 + 1

        qy0 = int(math.floor(y))
        qy1 = qy0 + 1

        v00 = self.values[self.getHashedIndex(qx0, qy0)]
        v01 = self.values[self.getHashedIndex(qx1, qy0)]
        v10 = self.values[self.getHashedIndex(qx0, qy1)]
        v11 = self.values[self.getHashedIndex(qx1, qy1)]

        tx = (x - math.floor(x))
        ty = (y - math.floor(y))

        return lerp(lerp(v00, v01, tx), lerp(v10, v11, tx), ty);

    def perlinNoise(self, x, y):
        qx0 = int(math.floor(x))
        qx1 = qx0 + 1

        qy0 = int(math.floor(y))
        qy1 = qy0 + 1

        q00 = self.getHashedIndex(qx0, qy0)
        q01 = self.getHashedIndex(qx1, qy0)
        q10 = self.getHashedIndex(qx0, qy1)
        q11 = self.getHashedIndex(qx1, qy1)

        tx0 = x - math.floor(x)
        tx1 = tx0 - 1

        ty0 = y - math.floor(y)
        ty1 = ty0 - 1

        v00 = self.gradients[q00][0] * tx0 + self.gradients[q00][1] * ty0
        v01 = self.gradients[q01][0] * tx1 + self.gradients[q01][1] * ty0
        v10 = self.gradients[q10][0] * tx0 + self.gradients[q10][1] * ty1
        v11 = self.gradients[q11][0] * tx1 + self.gradients[q11][1] * ty1

        wx = tx0 * tx0 * (3 - 2 * tx0)
        v0 = v00 + wx * (v01 - v00)
        v1 = v10 + wx * (v11 - v10)

        wy = ty0 * ty0 * (3 - 2 * ty0)
        return (v0 + wy * (v1 - v0)) * 0.5 + 1

    def makeTexture(self, texture = None):
        if texture is None:
            texture = self.cloud

        noise = {}
        max = min = None
        for i in range(self.imageSize):
            for j in range(self.imageSize):
                value = texture(i, j)
                noise[i, j] = value
                
                if max is None or max < value:
                    max = value

                if min is None or min > value:
                    min = value

        for i in range(self.imageSize):
            for j in range(self.imageSize):
                self.img[i, j] = (int) ((noise[i, j] - min) / (max - min) * 255 )

    def fractalBrownianMotion(self, x, y, func):
        octaves = 8
        amplitude = 1.0
        frequency = 1.0 / self.imageSize
        persistence = 0.5
        value = 0.0
        for k in range(octaves):
            value += func(x * frequency, y * frequency) * amplitude
            frequency *= 2
            amplitude *= persistence
        return value

    def value(self, x, y):
        return self.fractalBrownianMotion(4 * x, 4 * y, self.valueNoise)

    def cloud(self, x, y, func = None):
        if func is None:
            func = self.perlinNoise

        return self.fractalBrownianMotion(4 * x, 4 * y, func)

    def wood(self, x, y, noise = None):
        if noise is None:
            noise = self.perlinNoise

        frequency = 1.0 / self.imageSize
        n = noise(4 * x * frequency, 4 * y * frequency) * 10
        return n - int(n)

    def marble(self, x, y, noise = None):
        if noise is None:
            noise = self.perlinNoise

        frequency = 1.0 / self.imageSize
        n = self.fractalBrownianMotion(8 * x, 8 * y, self.perlinNoise)
        return (math.sin(16 * x * frequency + 4 * (n - 0.5)) + 1) * 0.5

if __name__ == "__main__":
    imageSize = 512
    noise = NoiseUtils(imageSize)
    noise.makeTexture(texture = noise.cloud)

    img = Image.new("L", (imageSize, imageSize))
    pixels = img.load()
    for i in range(0, imageSize):
       for j in range(0, imageSize):
            c = noise.img[i, j]
            pixels[i, j] = c
    img.save("temp.png")
