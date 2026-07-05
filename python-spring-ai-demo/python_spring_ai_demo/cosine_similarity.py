import math


class CosineSimilarity:
    @staticmethod
    def dot_product(vector_a: list[float], vector_b: list[float]) -> float:
        return sum(a * b for a, b in zip(vector_a, vector_b))

    @staticmethod
    def vector_magnitude(vector: list[float]) -> float:
        return math.sqrt(sum(component**2 for component in vector))

    @classmethod
    def cosine_similarity(cls, vector_a: list[float], vector_b: list[float]) -> float:
        magnitude_a = cls.vector_magnitude(vector_a)
        magnitude_b = cls.vector_magnitude(vector_b)
        if magnitude_a == 0 or magnitude_b == 0:
            return 0
        return cls.dot_product(vector_a, vector_b) / (magnitude_a * magnitude_b)
