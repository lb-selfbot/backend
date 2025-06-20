package middleware

import (
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/lb-selfbot/backend/internal/services/auth"
)

func authMiddleware(authService auth.Service) fiber.Handler {
	return func(c *fiber.Ctx) error {
		authHeader := c.Get("Authorization")
		if authHeader != "" && strings.HasPrefix(authHeader, "Bearer ") {
			token := authHeader[7:]
			if claims, err := authService.ValidateAccessToken(token); err == nil {
				c.Locals("claims", claims)
			}
		}
		return c.Next()
	}
}

func MustAuth() fiber.Handler {
	return func(ctx *fiber.Ctx) error {
		if ctx.Locals("claims") == nil {
			return ctx.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
				"error": "Invalid or expired token",
			})
		}
		return ctx.Next()
	}
}

func GetClaims(ctx *fiber.Ctx) *auth.Claims {
	claims := ctx.Locals("claims")
	if claims == nil {
		return nil
	}
	return claims.(*auth.Claims)
}
