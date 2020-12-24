#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include "sign.h"
#include "point.h"
#include "curve.h"
#include "serialization.h"


void sign_init(sign_ptr sign) {
    sign->data = NULL;
    sign->length = 0;
}

void sign_inits(sign_ptr sign1, ...) {
    va_list signs;
    sign_ptr sign;

    sign_init(sign1);
    va_start(signs, sign1);

    while ((sign = va_arg(signs, sign_ptr)) != NULL) {
        sign_init(sign);
    }

    va_end(signs);
}

void sign_clear(sign_ptr sign) {
    if (sign->data != NULL) {
        memset(sign->data, 0, sign->length);
    }

    free(sign->data);
    sign->data = NULL;
    sign->length = 0;
}

void sign_clears(sign_ptr sign1, ...) {
    va_list signs;
    sign_ptr sign;

    sign_clear(sign1);
    va_start(signs, sign1);

    while ((sign = va_arg(signs, sign_ptr)) != NULL) {
        sign_clear(sign);
    }

    va_end(signs);
}

void sign_set(sign_ptr result, sign_srcptr sign) {
    if (result->data != NULL) {
        free(result->data);
        result->data = NULL;
    }

    result->length = sign->length;
    
    if (sign->data != NULL) {
        result->data = malloc(result->length);
        memcpy(result->data, sign->data, result->length);
    }
}

bool sign_is_equal(sign_srcptr sign1, sign_srcptr sign2) {
    if (sign1->length != sign2->length) {
        return false;
    }

    if ((sign1->data == NULL) != (sign2->data == NULL)) {
        return false;
    }

    return (sign1->data == NULL && sign2->data == NULL)
        || memcmp(sign1->data, sign2->data, sign1->length) == 0;
}

void __sign_data_to_point(point_ptr point, mpz_srcptr N, size_t data_size, const uint8_t *data) {
    mpz_t x, y;
    size_t coord_length, value_length;
    uint8_t *value;

    coord_length = (mpz_sizeinbase(N, 2) - 1) / 8;
    value_length = 2 * coord_length * sizeof(uint8_t);

    value = malloc(value_length);
    memset(value, 0xFF, value_length);

    for (size_t i = 0, j = 0; i < data_size; i++, j++) {
        if (j == value_length) {
            j = 0;
        }

        value[j] ^= data[i];
    }

    mpz_inits(x, y, NULL);

    mpz_import(x, coord_length, LSB_FIRST, sizeof(uint8_t), NATIVE_ENDIANNESS, 0, value);
    mpz_import(y, coord_length, LSB_FIRST, sizeof(uint8_t), NATIVE_ENDIANNESS, 0, value + coord_length);

    mpz_set(point->x, x);
    mpz_set(point->y, y);

    mpz_clears(x, y, NULL);

    free(value);
}

void __sign_create_curve(curve_ptr curve, point_srcptr point, mpz_srcptr N) {
    mpz_t a, b, q, x, y;

    mpz_inits(a, b, q, x, y, NULL);

    // q = N
    mpz_set(q, N);

    // a = 0
    mpz_set_ui(a, 0);

    // y = (point->y^2) % q
    mpz_mul(y, point->y, point->y);
    mpz_mod(y, y, q);

    // x = (point->x^3) % q
    mpz_mul(x, point->x, point->x);
    mpz_mul(x, x, point->x);
    mpz_mod(x, x, q);

    // b = (y - x) % q
    mpz_sub(b, y, x);
    mpz_mod(b, b, q);

    mpz_set(curve->a, a);
    mpz_set(curve->b, b);
    mpz_set(curve->q, q);

    mpz_clears(a, b, q, x, y, NULL);
}

void __sign_exclude_identity(curve_ptr curve, point_ptr point, mpz_srcptr N) {
    const unsigned long default_x = 31337, default_y = 31337;

    if (point_is_identity(point) || !curve_is_valid(curve)) {
        mpz_set_ui(point->x, default_x);
        mpz_set_ui(point->y, default_y);

        __sign_create_curve(curve, point, N);
    }
}

void sign_create(sign_ptr sign, private_srcptr private, size_t data_size, const uint8_t *data) {
    size_t result_data_size;
    uint8_t *result_data;
    curve_t curve;
    point_t data_point, sign_point;

    curve_init(curve);
    point_inits(data_point, sign_point, NULL);

    __sign_data_to_point(data_point, private->N, data_size, data);
    __sign_create_curve(curve, data_point, private->N);
    __sign_exclude_identity(curve, data_point, private->N);
    
    point_multiply(sign_point, data_point, private->d, curve);

    mpzs_serialize(&result_data_size, &result_data, 2, sign_point->x, sign_point->y);

    sign->data = result_data;
    sign->length = result_data_size;

    point_clears(data_point, sign_point, NULL);
    curve_clear(curve);
}

bool sign_verify(sign_srcptr sign, public_srcptr public, size_t data_size, const uint8_t *data) {
    const unsigned long default_x = 31337, default_y = 31337;

    mpz_t *mpzs;
    size_t mpzs_count;
    curve_t curve;
    point_t data_point, data_point_expected, sign_point;
    bool result;

    result = false;
    mpzs_deserialize(&mpzs_count, &mpzs, sign->length, sign->data);

    if (mpzs_count == 2) {
        curve_init(curve);
        point_inits(data_point, data_point_expected, sign_point, NULL);

        mpz_set(sign_point->x, mpzs[0]);
        mpz_set(sign_point->y, mpzs[1]);

        if (!point_is_identity(sign_point)) {
            __sign_data_to_point(data_point, public->N, data_size, data);
            __sign_create_curve(curve, data_point, public->N);
            __sign_exclude_identity(curve, data_point, public->N);

            if (point_is_on_curve(sign_point, curve)) {
                point_multiply(data_point_expected, sign_point, public->e, curve);

                result = point_is_equal(data_point, data_point_expected);
            }
        }

        point_clears(data_point, data_point_expected, sign_point, NULL);
        curve_clear(curve);
    }

    for (size_t i = 0; i < mpzs_count; i++) {
        mpz_clear(mpzs[i]);
    }

    free(mpzs);

    return result;
}
