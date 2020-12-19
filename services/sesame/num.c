#include "types.h"


uint192 expand(uint64 n)
{
	uint192 r;
	r.i0 = 0;
	r.i1 = 0;
	r.i2 = n;

	return r;
}

uint192 add(uint192 a, uint64 b)
{
	uint128 t;
	uint192 r;

	t = (uint128)a.i2 + b;
	r.i2 = t;
	r.i1 = (t >> 64) + a.i1;
	r.i0 = a.i0;

	return r;
}

uint192 multiply(uint192 a, uint64 b)
{
	uint128 t;
	uint192 r;

	t = (uint128)a.i2 * b;
	r.i2 = t;
	t >>= 64;
	t += (uint128)a.i1 * b;
	r.i1 = t;
	t >>= 64;
	t += (uint128)a.i0 * b;
	r.i0 = t;

	return r;
}

uint192 divmod(uint192 a, uint32 b, uint32 *remainder)
{
	uint64 t;
	uint192 r;

	uint32 *ai = (uint32 *)&a;
	uint32 *ri = (uint32 *)&r;

	ri[5] = ai[5] / b;
	t = ((uint64)(ai[5] % b) << 32) | ai[4];
	ri[4] = t / b;
	t = ((uint64)(t % b) << 32) | ai[3];
	ri[3] = t / b;
	t = ((uint64)(t % b) << 32) | ai[2];
	ri[2] = t / b;
	t = ((uint64)(t % b) << 32) | ai[1];
	ri[1] = t / b;
	t = ((uint64)(t % b) << 32) | ai[0];
	ri[0] = t / b;
	*remainder = t % b;

	return r;
}

bool is_zero(uint192 n)
{
	return !n.i2 && !n.i1 && !n.i0; 
}

uint192 xor(uint192 a, uint192 b)
{
	a.i0 ^= b.i0;
	a.i1 ^= b.i1;
	a.i2 ^= b.i2;

	return a;
}

uint192 not(uint192 n)
{
	n.i0 = ~n.i0;
	n.i1 = ~n.i1;
	n.i2 = ~n.i2;

	return n;
}