import hashlib
import math


# LT Coding Helper fucntions:
class PRNG(object):
    """
    A Pseudorandom Number Generator that yields samples from the set of source
    blocks using the RSD degree distribution described above.
    """

    def __init__(self, params):
        """Provide RSD parameters on construction """
        self.state = None  # Seed is set by interfacing code using set_seed
        K, delta, c = params
        self.K = K
        self.cdf = self.__gen_rsd_cdf(K, delta, c)

    def __gen_tau(self, S, K, delta):
        """The Robust part of the RSD, we precompute an array for speed"""
        pivot = int(math.floor(K / S))
        return [S / K * 1 / d for d in range(1, pivot)] \
               + [S / K * math.log(S / delta)] \
               + [0 for d in range(pivot, K)]

    def __gen_rho(self, K):
        """The Ideal Soliton Distribution, we precompute an array for speed"""
        return [1 / K] + [1 / (d * (d - 1)) for d in range(2, K + 1)]

    def __gen_mu(self, K, delta, c):
        """The Robust Soliton Distribution on the degree of transmitted blocks"""
        S = c * math.log(K / delta) * math.sqrt(K)
        tau = self.__gen_tau(S, K, delta)
        rho = self.__gen_rho(K)
        normalizer = sum(rho) + sum(tau)
        return [(rho[d] + tau[d]) / normalizer for d in range(K)]

    def __gen_rsd_cdf(self, K, delta, c):
        """The CDF of the RSD on block degree, precomputed for sampling speed"""
        mu = self.__gen_mu(K, delta, c)
        return [sum(mu[:d + 1]) for d in range(K)]


    def _get_next(self):
        """Executes the next iteration of the PRNG evolution process, and returns the result"""
        PRNG_A = 16807
        PRNG_M = (1 << 31) - 1
        self.state = PRNG_A * self.state % PRNG_M
        return self.state

    def _sample_d(self):
        """Samples degree given the precomputed distributions above and the linear PRNG output """
        PRNG_M = (1 << 31) - 1
        PRNG_MAX_RAND = PRNG_M - 1
        p = self._get_next() / PRNG_MAX_RAND
        for ix, v in enumerate(self.cdf):
            if v > p:
                return ix + 1
        return ix + 1

    def set_seed(self, seed):
        """Reset the state of the PRNG to the given seed"""
        self.state = seed

    def get_src_blocks(self, seed=None):
        """
        Returns the indices of a set of `d` source blocks sampled from indices i = 1, ..., K-1 uniformly,
        where `d` is sampled from the RSD described above.
        """
        if seed:
            self.state = seed
        blockseed = self.state
        d = self._sample_d()
        have = 0
        nums = set()
        while have < d:
            num = self._get_next() % self.K
            if num not in nums:
                nums.add(num)
                have += 1
        return blockseed, d, nums


def get_sha256_hash_of_input_data_func(input_data_or_string):
    if isinstance(input_data_or_string, str):
        input_data_or_string = input_data_or_string.encode('utf-8')
    sha256_hash_of_input_data = hashlib.sha3_256(input_data_or_string).hexdigest()
    return sha256_hash_of_input_data
