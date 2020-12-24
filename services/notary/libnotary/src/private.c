#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include "private.h"
#include "serialization.h"


void private_init(private_ptr private) {
    mpz_inits(private->N, private->p, private->q, private->e, private->d, NULL);
}

void private_inits(private_ptr private1, ...) {
    va_list privates;
    private_ptr private;

    private_init(private1);
    va_start(privates, private1);

    while ((private = va_arg(privates, private_ptr)) != NULL) {
        private_init(private);
    }

    va_end(privates);
}

void private_clear(private_ptr private) {
    mpz_clears(private->N, private->p, private->q, private->e, private->d, NULL);
}

void private_clears(private_ptr private1, ...) {
    va_list privates;
    private_ptr private;

    private_clear(private1);
    va_start(privates, private1);

    while ((private = va_arg(privates, private_ptr)) != NULL) {
        private_clear(private);
    }

    va_end(privates);
}

void private_set(private_ptr result, private_srcptr private) {
    mpz_set(result->N, private->N);
    mpz_set(result->p, private->p);
    mpz_set(result->q, private->q);
    mpz_set(result->e, private->e);
    mpz_set(result->d, private->d);
}

bool private_is_equal(private_srcptr private1, private_srcptr private2) {
    return mpz_cmp(private1->N, private2->N) == 0
        && mpz_cmp(private1->p, private2->p) == 0
        && mpz_cmp(private1->q, private2->q) == 0
        && mpz_cmp(private1->e, private2->e) == 0
        && mpz_cmp(private1->d, private2->d) == 0;
}

void private_serialize(size_t *result_size, uint8_t **result, private_srcptr private) {
    mpzs_serialize(result_size, result, 5, private->N, private->p, private->q, private->e, private->d);
}

bool private_deserialize(private_ptr private, size_t data_size, const uint8_t *data) {
    mpz_t *mpzs;
    size_t mpzs_count;
    bool result;

    result = false;
    mpzs_deserialize(&mpzs_count, &mpzs, data_size, data);

    if (mpzs_count == 5) {
        mpz_set(private->N, mpzs[0]);
        mpz_set(private->p, mpzs[1]);
        mpz_set(private->q, mpzs[2]);
        mpz_set(private->e, mpzs[3]);
        mpz_set(private->d, mpzs[4]);
        
        result = true;
    }

    for (size_t i = 0; i < mpzs_count; i++) {
        mpz_clear(mpzs[i]);
    }

    free(mpzs);

    return result;
}

void private_get_public(public_ptr public, private_srcptr private) {
    mpz_set(public->N, private->N);
    mpz_set(public->e, private->e);
}

void __private_generate_prime(mpz_ptr prime, size_t bits, FILE *random) {
    const int32_t checks = 10;

    mpz_t result, remainder;
    uint64_t seed;
    gmp_randstate_t state;

    fread(&seed, sizeof(uint64_t), 1, random);

    gmp_randinit_mt(state);
    gmp_randseed_ui(state, seed);

    mpz_inits(result, remainder, NULL);

    do {
        mpz_rrandomb(result, state, bits);
        mpz_mod_ui(remainder, result, 3);
    } while (mpz_probab_prime_p(result, checks) == 0 || mpz_cmp_ui(remainder, 2) != 0);

    mpz_set(prime, result);

    mpz_clears(result, remainder, NULL);
    gmp_randclear(state);
}

bool private_generate(private_ptr private) {
    const size_t bits = 512;
    const unsigned long exponent = 65537;

    FILE *urandom;
    mpz_t N, p, q, e, d, phi;

    urandom = fopen("/dev/urandom", "r");
    if (urandom == NULL) {
        return false;
    }

    mpz_inits(N, p, q, e, d, phi, NULL);

    __private_generate_prime(p, bits, urandom);
    __private_generate_prime(q, bits, urandom);

    fclose(urandom);

    // e = exponent
    mpz_set_ui(e, exponent);
    
    // N = p * q
    mpz_mul(N, p, q);

    // phi = (p + 1) * (q + 1) = N + p + q + 1
    mpz_set(phi, N);
    mpz_add(phi, phi, p);
    mpz_add(phi, phi, q);
    mpz_add_ui(phi, phi, 1);

    // d = (e^-1) % phi
    mpz_invert(d, e, phi);

    mpz_set(private->N, N);
    mpz_set(private->p, p);
    mpz_set(private->q, q);
    mpz_set(private->e, e);
    mpz_set(private->d, d);

    mpz_clears(N, p, q, e, d, phi, NULL);

    return true;
}

bool private_is_valid(private_srcptr private) {
    const int32_t checks = 10;

    mpz_t N, phi, gcd, ed;
    bool result;

    result = true;

    mpz_inits(N, phi, gcd, ed, NULL);

    if (mpz_probab_prime_p(private->p, checks) == 0 || mpz_probab_prime_p(private->q, checks) == 0) {
        result = false;
    }

    // N = private->p * private->q
    mpz_mul(N, private->p, private->q);

    if (mpz_cmp(private->N, N) != 0) {
        result = false;
    }

    // phi = (private->p + 1) * (private->q + 1) = private->N + private->p + private->q + 1
    mpz_set(phi, private->N);
    mpz_add(phi, phi, private->p);
    mpz_add(phi, phi, private->q);
    mpz_add_ui(phi, phi, 1);

    if (mpz_cmp(private->e, phi) >= 0) {
        result = false;
    }

    mpz_gcd(gcd, private->e, phi);

    if (mpz_cmp_ui(gcd, 1) != 0) {
        result = false;
    }

    // ed = (private->e * private->d) % phi
    mpz_mul(ed, private->e, private->d);
    mpz_mod(ed, ed, phi);

    if (mpz_cmp_ui(ed, 1) != 0) {
        result = false;
    }

    mpz_clears(N, phi, gcd, ed, NULL);

    return result;
}
