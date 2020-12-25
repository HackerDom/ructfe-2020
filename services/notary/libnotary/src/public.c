#include <stdlib.h>
#include <stdarg.h>
#include "public.h"
#include "serialization.h"


void public_init(public_ptr public) {
    mpz_inits(public->N, public->e, NULL);
}

void public_inits(public_ptr public1, ...) {
    va_list publics;
    public_ptr public;

    public_init(public1);
    va_start(publics, public1);

    while ((public = va_arg(publics, public_ptr)) != NULL) {
        public_init(public);
    }

    va_end(publics);
}

void public_clear(public_ptr public) {
    mpz_clears(public->N, public->e, NULL);
}

void public_clears(public_ptr public1, ...) {
    va_list publics;
    public_ptr public;

    public_clear(public1);
    va_start(publics, public1);

    while ((public = va_arg(publics, public_ptr)) != NULL) {
        public_clear(public);
    }

    va_end(publics);
}

void public_set(public_ptr result, public_srcptr public) {
    mpz_set(result->N, public->N);
    mpz_set(result->e, public->e);
}

bool public_is_equal(public_srcptr public1, public_srcptr public2) {
    return mpz_cmp(public1->N, public2->N) == 0
        && mpz_cmp(public1->e, public2->e) == 0;
}

void public_serialize(size_t *result_size, uint8_t **result, public_srcptr public) {
    mpzs_serialize(result_size, result, 2, public->N, public->e);
}

bool public_deserialize(public_ptr public, size_t data_size, const uint8_t *data) {
    mpz_t *mpzs;
    size_t mpzs_count;
    bool result;

    result = false;
    mpzs_deserialize(&mpzs_count, &mpzs, data_size, data);

    if (mpzs_count == 2) {
        mpz_set(public->N, mpzs[0]);
        mpz_set(public->e, mpzs[1]);
        
        result = true;
    }

    for (size_t i = 0; i < mpzs_count; i++) {
        mpz_clear(mpzs[i]);
    }

    free(mpzs);

    return result;
}
