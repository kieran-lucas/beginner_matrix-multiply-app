class Matrix:
    def __init__(self, data):
        self.n = len(data)
        self.data = data
    def multiply(self, other):
        res = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                s = 0
                for k in range(self.n):
                    s += self.data[i][k] * other.data[k][j]
                row.append(s)
            res.append(row)
        return Matrix(res)
    def __repr__(self):
        return "\n".join(str(row) for row in self.data)
A = Matrix([
    [1, 2],
    [3, 4]
])
B = Matrix([
    [5, 6],
    [7, 8]
])
print(A.multiply(B))