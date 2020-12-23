#ifndef _CURVE_H
#define _CURVE_H

#include <gmp.h>
#include <stdint.h>
#include <stdbool.h>


typedef struct {
    mpz_t a;
    mpz_t b;
    mpz_t q;
} __curve_struct;

typedef __curve_struct curve_t[1];
typedef __curve_struct *curve_ptr;
typedef const __curve_struct *curve_srcptr;

void curve_init(curve_ptr curve);
void curve_inits(curve_ptr curve1, ...);
void curve_clear(curve_ptr curve);
void curve_clears(curve_ptr curve1, ...);
void curve_set(curve_ptr result, curve_srcptr curve);
bool curve_is_equal(curve_srcptr curve1, curve_srcptr curve2);

void curve_serialize(size_t *result_size, uint8_t **result, curve_srcptr curve);
bool curve_deserialize(curve_ptr curve, size_t data_size, const uint8_t *data);

bool curve_is_valid(curve_srcptr curve);


#endif
