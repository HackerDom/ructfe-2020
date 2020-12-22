#include <stdarg.h>
#include "curve.h"


void curve_init(curve_ptr curve) {
    mpz_inits(curve->a, curve->b, curve->q, NULL);
}

void curve_inits(curve_ptr curve1, ...) {
    va_list curves;
    curve_ptr curve;

    curve_init(curve1);
    va_start(curves, curve1);

    while ((curve = va_arg(curves, curve_ptr)) != NULL) {
        curve_init(curve);
    }

    va_end(curves);
}

void curve_clear(curve_ptr curve) {
    mpz_clears(curve->a, curve->b, curve->q, NULL);
}

void curve_clears(curve_ptr curve1, ...) {
    va_list curves;
    curve_ptr curve;

    curve_clear(curve1);
    va_start(curves, curve1);

    while ((curve = va_arg(curves, curve_ptr)) != NULL) {
        curve_clear(curve);
    }

    va_end(curves);
}

void curve_set(curve_ptr result, curve_srcptr curve) {
    mpz_set(result->a, curve->a);
    mpz_set(result->b, curve->b);
    mpz_set(result->q, curve->q);
}

bool curve_is_equal(curve_srcptr curve1, curve_srcptr curve2) {
    return mpz_cmp(curve1->a, curve2->a) == 0
        && mpz_cmp(curve1->b, curve2->b) == 0
        && mpz_cmp(curve1->q, curve2->q) == 0;
}

bool curve_is_correct(curve_srcptr curve) {
    mpz_t a, b, sum;
    bool result;

    mpz_inits(a, b, sum, NULL);

    // a = 4 * curve->a^3
    mpz_pow_ui(a, curve->a, 3);
    mpz_mul_ui(a, a, 4);

    // b = 27 * curve->b^2
    mpz_pow_ui(b, curve->b, 2);
    mpz_mul_ui(b, b, 27);

    // sum = (a + b) % curve->q
    mpz_add(sum, a, b);
    mpz_mod(sum, sum, curve->q);
    
    result = mpz_cmp_ui(sum, 0) == 0 
        && mpz_cmp_ui(curve->q, 2) >= 0;

    mpz_clears(a, b, sum, NULL);

    return result;
}
