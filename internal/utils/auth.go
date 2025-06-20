package utils

import (
	"errors"

	"github.com/gofiber/fiber/v2"
	"github.com/lb-selfbot/backend/internal/services/auth"
)

var (
	ErrUserNotAuthenticated = errors.New("user not authenticated")
	ErrInvalidUserContext   = errors.New("invalid user context")
)

// GetUserID extracts the user ID from the Fiber context
func GetUserID(c *fiber.Ctx) (int, error) {
	userID := c.Locals("user_id")
	if userID == nil {
		return 0, ErrUserNotAuthenticated
	}

	id, ok := userID.(int)
	if !ok {
		return 0, ErrInvalidUserContext
	}

	return id, nil
}

// GetUsername extracts the username from the Fiber context
func GetUsername(c *fiber.Ctx) (string, error) {
	username := c.Locals("username")
	if username == nil {
		return "", ErrUserNotAuthenticated
	}

	name, ok := username.(string)
	if !ok {
		return "", ErrInvalidUserContext
	}

	return name, nil
}

// GetClaims extracts the JWT claims from the Fiber context
func GetClaims(c *fiber.Ctx) (*auth.Claims, error) {
	claims := c.Locals("claims")
	if claims == nil {
		return nil, ErrUserNotAuthenticated
	}

	authClaims, ok := claims.(*auth.Claims)
	if !ok {
		return nil, ErrInvalidUserContext
	}

	return authClaims, nil
}

// MustGetUserID is like GetUserID but panics on error (use with auth middleware)
func MustGetUserID(c *fiber.Ctx) int {
	id, err := GetUserID(c)
	if err != nil {
		panic(err)
	}
	return id
}

// MustGetUsername is like GetUsername but panics on error (use with auth middleware)
func MustGetUsername(c *fiber.Ctx) string {
	username, err := GetUsername(c)
	if err != nil {
		panic(err)
	}
	return username
}

// MustGetClaims is like GetClaims but panics on error (use with auth middleware)
func MustGetClaims(c *fiber.Ctx) *auth.Claims {
	claims, err := GetClaims(c)
	if err != nil {
		panic(err)
	}
	return claims
}
