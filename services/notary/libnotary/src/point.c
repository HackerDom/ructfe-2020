#include <stdlib.h>
#include <stdarg.h>
#include "point.h"
#include "serialization.h"


void point_init(point_ptr point) {
    mpz_inits(point->x, point->y, NULL);
}

void point_inits(point_ptr point1, ...) {
    va_list points;
    point_ptr point;

    point_init(point1);
    va_start(points, point1);

    while ((point = va_arg(points, point_ptr))) {
        point_init(point);
    }

    va_end(points);
}

void point_clear(point_ptr point) {
    mpz_clears(point->x, point->y, NULL);
}

void point_clears(point_ptr point1, ...) {
    va_list points;
    point_ptr point;

    point_clear(point1);
    va_start(points, point1);

    while ((point = va_arg(points, point_ptr))) {
        point_clear(point);
    }

    va_end(points);
}

void point_set(point_ptr result, point_srcptr point) {
    mpz_set(result->x, point->x);
    mpz_set(result->y, point->y);
}

bool point_is_equal(point_srcptr point1, point_srcptr point2) {
    return mpz_cmp(point1->x, point2->x) == 0
        && mpz_cmp(point1->y, point2->y) == 0;
}

void point_serialize(size_t *result_size, uint8_t **result, point_srcptr point) {
    mpzs_serialize(result_size, result, 2, point->x, point->y);
}

bool point_deserialize(point_ptr point, size_t data_size, const uint8_t *data) {
    mpz_t *mpzs;
    size_t mpzs_count;
    bool result;

    result = false;
    mpzs_deserialize(&mpzs_count, &mpzs, data_size, data);

    if (mpzs_count == 2) {
        mpz_set(point->x, mpzs[0]);
        mpz_set(point->y, mpzs[1]);
        
        result = true;
    }

    for (size_t i = 0; i < mpzs_count; i++) {
        mpz_clear(mpzs[i]);
    }

    free(mpzs);

    return result;
}

void point_set_identity(point_ptr point) {
    mpz_set_ui(point->x, 0);
    mpz_set_ui(point->y, 0);
}

void point_inverse(point_ptr result, point_srcptr point, curve_srcptr curve) {
    mpz_t x, y;

    mpz_inits(x, y, NULL);

    // x = point->x
    mpz_set(x, point->x);

    // y = (-point->y) % curve->q
    mpz_neg(y, point->y);
    mpz_mod(y, y, curve->q);

    mpz_set(result->x, x);
    mpz_set(result->y, y);

    mpz_clears(x, y, NULL);
}

void point_add(point_ptr result, point_srcptr point1, point_srcptr point2, curve_srcptr curve) {
    mpz_t lambda, x, y, t1, t2;

    if (point_is_identity(point1)) {
        point_set(result, point2);
        return;
    }

    if (point_is_identity(point2)) {
        point_set(result, point1);
        return;
    }

    if (mpz_cmp(point1->x, point2->x) == 0 && (mpz_cmp(point1->y, point2->y) != 0 || mpz_cmp_ui(point1->y, 0) == 0)) {
        point_set_identity(result);
        return;
    }

    mpz_inits(lambda, x, y, t1, t2, NULL);

    if (mpz_cmp(point1->x, point2->x) == 0) {
        // t1 = (3 * point1->x * point1->x + curve->a) % curve->q
        mpz_set_ui(t1, 3);
        mpz_mul(t1, t1, point1->x);
        mpz_mul(t1, t1, point1->x);
        mpz_add(t1, t1, curve->a);
        mpz_mod(t1, t1, curve->q);

        // t2 = ((2 * point1->y)^-1) % curve->q
        mpz_set_ui(t2, 2);
        mpz_mul(t2, t2, point1->y);
        mpz_invert(t2, t2, curve->q);
    }
    else {
        // t1 = (point1->y - point2->y) % curve->q
        mpz_sub(t1, point1->y, point2->y);
        mpz_mod(t1, t1, curve->q);

        // t2 = ((point1->x - point2->x)^-1) % curve->q
        mpz_sub(t2, point1->x, point2->x);
        mpz_invert(t2, t2, curve->q);
    }

    // lambda = (t1 * t2) % curve->q
    mpz_mul(lambda, t1, t2);
    mpz_mod(lambda, lambda, curve->q);

    // x = (lambda * lambda - point1->x - point2->x) % curve->q
    mpz_mul(x, lambda, lambda);
    mpz_sub(x, x, point1->x);
    mpz_sub(x, x, point2->x);
    mpz_mod(x, x, curve->q);

    // y = (lambda * (point1->x - x) - point1->y) % curve->q
    mpz_sub(y, point1->x, x);
    mpz_mul(y, y, lambda);
    mpz_sub(y, y, point1->y);
    mpz_mod(y, y, curve->q);

    mpz_set(result->x, x);
    mpz_set(result->y, y);

    mpz_clears(lambda, x, y, t1, t2, NULL);
}

void point_double(point_ptr result, point_srcptr point, curve_srcptr curve) {
    point_add(result, point, point, curve);
}

void point_multiply(point_ptr result, point_srcptr point, mpz_srcptr number, curve_srcptr curve) {
    size_t size;
    point_t r0, r1;
    mpz_t multiplier;

    point_inits(r0, r1, NULL);
    point_set_identity(r0);
    point_set(r1, point);

    mpz_init_set(multiplier, number);

    if (mpz_sgn(multiplier) < 0) {
        point_inverse(r1, r1, curve);
        mpz_abs(multiplier, multiplier);
    }

    size = mpz_sizeinbase(curve->q, 2);

    for (size_t i = 0; i < size; i++) {
        if (mpz_tstbit(number, size - i - 1) == 1) {
            point_add(r0, r0, r1, curve);
            point_double(r1, r1, curve);
        }
        else {
            point_add(r1, r0, r1, curve);
            point_double(r0, r0, curve);
        }
    }

    point_set(result, r0);

    mpz_clear(multiplier);
    point_clears(r0, r1, NULL);
}

bool point_is_identity(point_srcptr point) {
    return mpz_cmp_ui(point->x, 0) == 0
        && mpz_cmp_ui(point->y, 0) == 0;
}

bool point_is_on_curve(point_srcptr point, curve_srcptr curve) {
    mpz_t y2, x3, x, sum;
    bool result;

    mpz_inits(y2, x3, x, sum, NULL);

    // y2 = (point->y^2) % curve->q
    mpz_powm_ui(y2, point->y, 2, curve->q);

    // x3 = (point->x^3) % curve->q
    mpz_powm_ui(x3, point->x, 3, curve->q);

    // x = (curve->a * point->x) % curve->q
    mpz_mul(x, curve->a, point->x);
    mpz_mod(x, x, curve->q);

    // sum = (y2 - x3 - x - curve->b) % curve->q
    mpz_sub(sum, y2, x3);
    mpz_sub(sum, sum, x);
    mpz_sub(sum, sum, curve->b);
    mpz_mod(sum, sum, curve->q);

    result = mpz_cmp_ui(sum, 0) == 0;

    mpz_clears(y2, x3, x, sum, NULL);

    return result;
}
