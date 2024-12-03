from typing import List, Tuple, Union
import math
import numpy as np


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
        return type(self)([a + b for a, b in zip(self.v, other.v)])
    
    def __sub__(self, other):
        """Subtract another vector from this vector."""
        if not isinstance(other, Vector):
            raise ValueError("Can only subtract another Vector.")
        if len(self) != len(other):
            raise ValueError("Vectors must be the same length for subtraction.")
        return type(self)([a - b for a, b in zip(self.v, other.v)])

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
        return type(self)([x / other for x in self.v])

    def __matmul__(self, other):
        """Perform matrix-vector multiplication using the @ operator."""
        if isinstance(other, np.ndarray):
            if other.ndim != 2:
                raise ValueError("Matrix must be 2-dimensional.")
            if other.shape[1] != len(self):
                raise ValueError("Matrix column count must match vector length.")
            # Convert vector to a NumPy array for compatibility, perform multiplication
            result = np.dot(other, np.array(self.values))
            return type(self)(result.tolist())
        raise ValueError("Can only multiply a vector with a 2D NumPy matrix.")

    def scale(self, constant):
        """Scale the vector by a constant."""
        if not isinstance(constant, (int, float)):
            raise ValueError("The scaling factor must be a numeric value.")
        return type(self)([x * constant for x in self.v])

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
        return type(self)([scale * x for x in other.v])

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
        return type(self)([
            b * f - c * e,
            c * d - a * f,
            a * e - b * d
        ])

class Vect2d(Vector):
    '''
    Special case of a vector in 2-dimensions
    '''
    def __init__(self, x:Union[float, List[float]], y:float=None):
        # Case 1: x is a list/tuple (x,y)
        if isinstance(x, list) or isinstance(x, tuple):
            if len(x) != 2:
                raise Exception('The length of a 2d vector must be 2.')
            super().__init__(x)
        else: # Case 2: x and y are numbers
            super().__init__([x, y])

        # Check that the vector 

    def rotate(self, theta:float) -> 'Vect2d':
        """Rotate the 2D vector by an angle theta (in degrees) around the origin."""
        # Apply a rotation matrix
        x, y = self.v
        theta_radians = math.radians(theta)
        cos_theta = math.cos(theta_radians)
        sin_theta = math.sin(theta_radians)
        new_x = x * cos_theta - y * sin_theta
        new_y = x * sin_theta + y * cos_theta
        return Vect2d([new_x, new_y])
