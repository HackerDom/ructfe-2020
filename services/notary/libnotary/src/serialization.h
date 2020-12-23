#ifndef _SERIALIZATION_H
#define _SERIALIZATION_H

#include <gmp.h>
#include <stdint.h>


#define LSB_FIRST -1
#define NATIVE_ENDIANNESS 0

void mpzs_serialize(size_t *data_size, uint8_t **data, size_t mpzs_count, ...);
void mpzs_deserialize(size_t *mpzs_count, mpz_t **mpzs, size_t data_size, const uint8_t *data);


#endif
