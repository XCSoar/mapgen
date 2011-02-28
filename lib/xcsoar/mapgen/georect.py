class GeoRect:
    def __init__(self, left = 0, right = 0, top = 0, bottom = 0):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def __str__(self):
        return 'left={}, right={}, top={}, bottom={}'.format(self.left, self.right, self.top, self.bottom)

    def height(self):
        return self.top - self.bottom

    def width(self):
        return self.right - self.left

    def intersects(self, other):
        return (self.inside(other.top, other.left) or
                self.inside(other.top, other.right) or
                self.inside(other.bottom, other.left) or
                self.inside(other.bottom, other.right) or
                other.inside(self.top, self.left) or
                other.inside(self.top, self.right) or
                other.inside(self.bottom, self.left) or
                other.inside(self.bottom, self.right))

    def inside(self, y, x):
        return y <= self.top and y >= self.bottom and x <= self.right and x >= self.left
