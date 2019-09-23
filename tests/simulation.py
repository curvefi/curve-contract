class Curve:
    def __init__(self, A, D, n):
        """
        A: Amplification coefficient
        D: Total deposit size
        n: number of currencies
        """
        self.A = A  # actually A * n ** (n - 1) because it's an invariant
        self.n = n
        self.x = [D // n] * n
        self.fee = 0.001

    def D(self):
        """
        D invariant calculation in non-overflowing integer operations
        iteratively

        A * sum(x_i) * n**n + D = A * D * n**n + D**(n+1) / (n**n * prod(x_i))

        Converging solution:
        D[j+1] = (A * n**n * sum(x_i) - D[j]**(n+1) / (n**n prod(x_i))) / (A * n**n - 1)
        """
        Dprev = 0
        S = sum(self.x)
        D = S
        Ann = self.A * self.n
        while abs(D - Dprev) > 1:
            D_P = D
            for x in self.x:
                D_P = D_P * D // (self.n * x)
            Dprev = D
            D = (Ann * S + D_P * self.n) * D // ((Ann - 1) * D + (self.n + 1) * D_P)
        return D

    def y(self, i, j, x):
        """
        Calculate x[j] if one makes x[i] = x

        Done by solving quadratic equation iteratively.
        x_1**2 + x1 * (sum' - (A*n**n - 1) * D / (A * n**n)) = D ** (n + 1) / (n ** (2 * n) * prod' * A)
        x_1**2 + b*x_1 = c

        x_1 = (x_1**2 + c) / (2*x_1 + b)
        """
        D = self.D()
        xx = [self.x[k] for k in range(self.n) if k not in (i, j)] + [x]
        Ann = self.A * self.n
        c = D
        for y in xx:
            c = c * D // (y * self.n)
        c = c * D // (self.n * Ann)
        b = sum(xx) + D // Ann - D
        y_prev = 0
        y = D
        while abs(y - y_prev) > 1:
            y_prev = y
            y = (y ** 2 + c) // (2 * y + b)
        return y

    def dy(self, i, j, dx):
        return self.x[j] - self.y(i, j, self.x[i] + dx)

    def exchange(self, i, j, dx):
        x = self.x[i] + dx
        y = self.y(i, j, x)
        dy = self.x[j] - y
        fee = int(dy * self.fee)
        assert dy > 0
        self.x[i] = x
        self.x[j] = y + fee
        return dy - fee
