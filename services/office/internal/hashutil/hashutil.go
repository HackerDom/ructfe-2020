package hashutil

import (
	"crypto/sha1"
	"encoding/binary"
	"encoding/hex"
	"math/rand"
)

func RandDigest(s string) string {
	randN := rand.Uint32()
	hash := sha1.New()
	bs := make([]byte, 4)
	binary.LittleEndian.PutUint32(bs, randN)
	hash.Write([]byte(s))
	hash.Write(bs)
	digest := hash.Sum(make([]byte, 0))
	return hex.EncodeToString(digest)
}
