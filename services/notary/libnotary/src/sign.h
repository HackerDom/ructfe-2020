#ifndef _SIGN_H
#define _SIGN_H

#include <gmp.h>
#include <stdint.h>
#include <stdbool.h>
#include "public.h"
#include "private.h"


typedef struct {
    size_t length;
    uint8_t *data;
} __sign_struct;

typedef __sign_struct sign_t[1];
typedef __sign_struct *sign_ptr;
typedef const __sign_struct *sign_srcptr;

void sign_init(sign_ptr sign);
void sign_inits(sign_ptr sign1, ...);
void sign_clear(sign_ptr sign);
void sign_clears(sign_ptr sign1, ...);
void sign_set(sign_ptr result, sign_srcptr sign);
bool sign_is_equal(sign_srcptr sign1, sign_srcptr sign2);

void sign_create(sign_ptr sign, private_srcptr private, size_t data_size, const uint8_t *data);
bool sign_verify(sign_srcptr sign, public_srcptr public, size_t data_size, const uint8_t *data);


#endif
