#ifndef _PRIVATE_H
#define _PRIVATE_H

#include <gmp.h>
#include <stdint.h>
#include <stdbool.h>
#include "public.h"


typedef struct {
    mpz_t N;
    mpz_t p;
    mpz_t q;
    mpz_t e;
    mpz_t d;
} __private_struct;

typedef __private_struct private_t[1];
typedef __private_struct *private_ptr;
typedef const __private_struct *private_srcptr;

void private_init(private_ptr private);
void private_inits(private_ptr private1, ...);
void private_clear(private_ptr private);
void private_clears(private_ptr private1, ...);
void private_set(private_ptr result, private_srcptr private);
bool private_is_equal(private_srcptr private1, private_srcptr private2);

void private_serialize(size_t *result_size, uint8_t **result, private_srcptr private);
bool private_deserialize(private_ptr private, size_t data_size, const uint8_t *data);

void private_get_public(public_ptr public, private_srcptr private);
bool private_generate(private_ptr private);
bool private_is_valid(private_srcptr private);
bool private_is_public_correct(private_srcptr private, public_srcptr public);


#endif
