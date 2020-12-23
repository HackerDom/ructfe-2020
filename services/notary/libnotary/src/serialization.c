#define _GNU_SOURCE

#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include "serialization.h"


void mpzs_serialize(size_t *data_size, uint8_t **data, size_t mpzs_count, ...) {
    size_t result_data_size, n_size_sum, n_size[mpzs_count];
    uint8_t *result_data, *n_data[mpzs_count];
    va_list mpzs;
    mpz_srcptr n;

    va_start(mpzs, mpzs_count);
    n_size_sum = 0;

    for (size_t i = 0; i < mpzs_count; i++) {
        n = va_arg(mpzs, mpz_srcptr);

        n_data[i] = mpz_export(NULL, &(n_size[i]), LSB_FIRST, sizeof(uint8_t), NATIVE_ENDIANNESS, 0, n);
        n_size_sum += n_size[i];
    }

    va_end(mpzs);

    result_data_size = sizeof(uint32_t) * mpzs_count + n_size_sum;
    result_data = malloc(result_data_size);

    for (size_t i = 0, j = 0; i < mpzs_count; i++) {
        *(uint32_t*)(result_data + j) = n_size[i];
        j += sizeof(uint32_t);

        memcpy(result_data + j, n_data[i], n_size[i]);
        j += n_size[i];

        free(n_data[i]);
    }

    memfrob(result_data, result_data_size);

    *data_size = result_data_size;
    *data = result_data;
}

void mpzs_deserialize(size_t *mpzs_count, mpz_t **mpzs, size_t data_size, const uint8_t *data) {
    mpz_t *ns, *result;
    size_t n_size, ns_count;
    uint8_t *clean_data;

    clean_data = malloc(data_size);
    memcpy(clean_data, data, data_size);
    memfrob(clean_data, data_size);

    ns_count = 0;
    ns = malloc(sizeof(mpz_t) * (data_size / sizeof(uint32_t)));

    for (size_t i = 0, j = 0; j < data_size; i++) {
        n_size = *(uint32_t*)(clean_data + j);
        j += sizeof(uint32_t);

        if (j + n_size > data_size) {
            break;
        }

        mpz_init(ns[i]);
        mpz_import(ns[i], n_size, LSB_FIRST, sizeof(uint8_t), NATIVE_ENDIANNESS, 0, clean_data + j);
        j += n_size;
        ns_count++;
    }

    result = malloc(sizeof(mpz_t) * ns_count);

    for (size_t i = 0; i < ns_count; i++) {
        mpz_init_set(result[i], ns[i]);
        mpz_clear(ns[i]);
    }

    free(ns);
    free(clean_data);

    *mpzs_count = ns_count;
    *mpzs = result;
}
