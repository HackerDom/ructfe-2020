#ifndef _POINT_H
#define _POINT_H

#include <gmp.h>
#include <stdint.h>
#include <stdbool.h>
#include "curve.h"


typedef struct {
    mpz_t x;
    mpz_t y;
} __point_struct;

typedef __point_struct point_t[1];
typedef __point_struct *point_ptr;
typedef const __point_struct *point_srcptr;

void point_init(point_ptr point);
void point_inits(point_ptr point1, ...);
void point_clear(point_ptr point);
void point_clears(point_ptr point1, ...);
void point_set(point_ptr result, point_srcptr point);
bool point_is_equal(point_srcptr point1, point_srcptr point2);

void point_serialize(size_t *result_size, uint8_t **result, point_srcptr point);
bool point_deserialize(point_ptr point, size_t data_size, const uint8_t *data);

void point_set_identity(point_ptr point);
void point_inverse(point_ptr result, point_srcptr point, curve_srcptr curve);
void point_add(point_ptr result, point_srcptr point1, point_srcptr point2, curve_srcptr curve);
void point_double(point_ptr result, point_srcptr point, curve_srcptr curve);
void point_multiply(point_ptr result, point_srcptr point, mpz_srcptr number, curve_srcptr curve);
bool point_is_identity(point_srcptr point);
bool point_is_on_curve(point_srcptr point, curve_srcptr curve);


#endif
