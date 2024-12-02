from typing import List, Tuple, Union
import math


class Vector:
    def __init__(self,
                 values:Union[List, Tuple]):
        self.v = list(values[0])

    def __repr__(self):
        return f"Vector({self.values}"

    def __setitem__(self, key, value):
        self.values[key] = value

    def __getitem__(self, key):
        return self.values[key]

    def __len__(self):
        return len(self.values)

    def __eq__(self, other):
        if isinstance(other, Vector):
            return self.values == other.values
        return False
    
    def append(self, value):
        self.values.append(value)

    def to_list(self):
        return list(self.values)

    def magnitude(self):
        """Calculate the magnitude of the vector."""
        return math.sqrt(sum(x ** 2 for x in self.values))

    def __add__(self, other):
        """Add twwo vectors"""
        if not isinstance(other, Vector):
            raise ValueError("Can only add another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for addition.")
        return Vector([a + b for a, b in zip(self.values, other.values)])
    
    def __sub__(self, other):
        """Subtract another vector from this vector."""
        if not isinstance(other, Vector):
            raise ValueError("Can only subtract another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for subtraction.")
        return Vector([a - b for a, b in zip(self.values, other.values)])

    def __mul__(self, other):
        """Scale the vector by a constant using the * operator."""
        if isinstance(other, (int, float)):
            return self.scale(other)

    def __rmul__(self, other):
        """Allow scalar * vector (commutative multiplication)."""
        return self.__mul__(other)

    def scale(self, constant):
        """Scale the vector by a constant."""
        if not isinstance(constant, (int, float)):
            raise ValueError("The scaling factor must be a numeric value.")
        return Vector([x * constant for x in self.values])

    def dot(self, other):
        """Calculate the dot product of two vectors."""
        if not isinstance(other, Vector):
            raise ValueError("Can only calculate dot product with another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for dot product.")
        return sum(a * b for a, b in zip(self.values, other.values))

    def projection(self, other):
        """Calculate the projection of this vector onto another vector."""
        if not isinstance(other, Vector):
            raise ValueError("Can only project onto another Vector.")
        magnitude_squared = other.magnitude() ** 2
        if magnitude_squared == 0:
            raise ValueError("Cannot project onto a zero vector.")
        scale = self.dot(other) / magnitude_squared
        return Vector([scale * x for x in other.values])

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
        a, b, c = self.values
        d, e, f = other.values
        return Vector([
            b * f - c * e,
            c * d - a * f,
            a * e - b * d
        ], immutable=self.immutable)