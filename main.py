n = int(input())
A = []
B = []
for i in range(n):
    rowA = list(map(int, input().split()))
    A.append(rowA)

for i in range(n):
    rowB = list(map(int, input().split()))
    B.append(rowB)

C = [[sum(A[i][k]*B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


for row in C:
    print(row)