from typing import List, Tuple, Union
import math


class Vector:
    def __init__(self,
                 values:Union[List, Tuple]):
        self.v = list(values)

    def __repr__(self):
        return f"Vector({self.v}"

    def __setitem__(self, key, value):
        self.v[key] = value

    def __getitem__(self, key):
        return self.v[key]

    def __len__(self):
        return len(self.v)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.v == other.v
        return False
    
    def append(self, value):
        self.v.append(value)

    def to_list(self):
        return list(self.v)

    def magnitude(self):
        """Calculate the magnitude of the vector."""
        return math.sqrt(sum(x ** 2 for x in self.v))

    def __add__(self, other):
        """Add twwo vectors"""
        if not isinstance(other, Vector):
            raise ValueError("Can only add another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for addition.")
        return Vector([a + b for a, b in zip(self.v, other.v)])
    
    def __sub__(self, other):
        """Subtract another vector from this vector."""
        if not isinstance(other, Vector):
            raise ValueError("Can only subtract another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for subtraction.")
        return Vector([a - b for a, b in zip(self.v, other.v)])

    def __mul__(self, other):
        """Scale the vector by a constant using the * operator."""
        if isinstance(other, (int, float)):
            return self.scale(other)

    def __rmul__(self, other):
        """Allow scalar * vector (commutative multiplication)."""
        return self.__mul__(other)

    def __truediv__(self, other):
        """Scale the vector by dividing each component by a constant using the / operator."""
        if not isinstance(other, (int, float)):
            raise ValueError("Can only divide a vector by a scalar (int or float).")
        if other == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return Vector([x / other for x in self.v])

    def scale(self, constant):
        """Scale the vector by a constant."""
        if not isinstance(constant, (int, float)):
            raise ValueError("The scaling factor must be a numeric value.")
        return Vector([x * constant for x in self.v])

    def dot(self, other):
        """Calculate the dot product of two vectors."""
        if not isinstance(other, Vector):
            raise ValueError("Can only calculate dot product with another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for dot product.")
        return sum(a * b for a, b in zip(self.v, other.v))

    def projection(self, other):
        """Calculate the projection of this vector onto another vector."""
        if not isinstance(other, Vector):
            raise ValueError("Can only project onto another Vector.")
        magnitude_squared = other.magnitude() ** 2
        if magnitude_squared == 0:
            raise ValueError("Cannot project onto a zero vector.")
        scale = self.dot(other) / magnitude_squared
        return Vector([scale * x for x in other.v])

    def angle(self, other):
        """Calculate the angle (in radians) between this vector and another."""
        if not isinstance(other, Vector):
            raise ValueError("Can only calculate angle with another Vector.")
        if self.magnitude() == 0 or other.magnitude() == 0:
            raise ValueError("Cannot calculate angle with a zero vector.")
        dot_product = self.dot(other)
        magnitudes = self.magnitude() * other.magnitude()
        cos_theta = max(-1, min(1, dot_product / magnitudes)) # Clamp to avoid numerical issues
        return math.acos(cos_theta)
    
    def cross(self, other):
        """Calculate the cross product of two 3D vectors."""
        if not isinstance(other, Vector):
            raise ValueError("Can only calculate cross product with another Vector.")
        if len(self) != 3 or len(other) != 3:
            raise ValueError("Cross product is only defined for 3D vectors.")
        a, b, c = self.v
        d, e, f = other.v
        return Vector([
            b * f - c * e,
            c * d - a * f,
            a * e - b * d
        ], immutable=self.immutable)