#ifndef _PUBLIC_H
#define _PUBLIC_H

#include <gmp.h>
#include <stdint.h>
#include <stdbool.h>


typedef struct {
    mpz_t N;
    mpz_t e;
} __public_struct;

typedef __public_struct public_t[1];
typedef __public_struct *public_ptr;
typedef const __public_struct *public_srcptr;

void public_init(public_ptr public);
void public_inits(public_ptr public1, ...);
void public_clear(public_ptr public);
void public_clears(public_ptr public1, ...);
void public_set(public_ptr result, public_srcptr public);
bool public_is_equal(public_srcptr public1, public_srcptr public2);

void public_serialize(size_t *result_size, uint8_t **result, public_srcptr public);
bool public_deserialize(public_ptr public, size_t data_size, const uint8_t *data);


#endif
