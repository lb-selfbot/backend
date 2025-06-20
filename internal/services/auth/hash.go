package auth

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"strings"

	"golang.org/x/crypto/argon2"
)

const (
	timeCost    = 1
	memoryCost  = 64 * 1024
	parallelism = 4
	keyLength   = 32
)

// HashArgon2 hashes the given password using argon2id.
func HashArgon2(password string) (string, error) {
	salt := make([]byte, 16)
	_, err := rand.Read(salt)
	if err != nil {
		return "", err
	}

	hash := argon2.IDKey([]byte(password), salt, timeCost, memoryCost, parallelism, keyLength)

	return fmt.Sprintf("$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s",
		argon2.Version, memoryCost, timeCost, parallelism,
		base64.RawStdEncoding.EncodeToString(salt),
		base64.RawStdEncoding.EncodeToString(hash)), nil
}

// VerifyArgon2 verifies the given password against the stored hash.
func VerifyArgon2(password, hash string) bool {
	parts := strings.Split(hash, "$")
	if len(parts) != 6 {
		return false
	}

	if parts[1] != "argon2id" || parts[2] != fmt.Sprintf("v=%d", argon2.Version) {
		return false
	}

	salt, _ := base64.RawStdEncoding.DecodeString(parts[4])
	expectedHash, _ := base64.RawStdEncoding.DecodeString(parts[5])

	actualHash := argon2.IDKey([]byte(password), salt, timeCost, memoryCost, parallelism, keyLength)

	return subtle.ConstantTimeCompare(expectedHash, actualHash) == 1
}
