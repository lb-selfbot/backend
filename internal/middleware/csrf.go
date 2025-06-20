package middleware

import (
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/csrf"
	"github.com/gofiber/storage/memory/v2"
	"github.com/lb-selfbot/backend/internal/services"
)

var csrfStorage = memory.New()

var csrfMiddleware = csrf.New(csrf.Config{
	CookieSameSite: "Strict",
	Storage:        csrfStorage,
})

// The RequireCSRF middleware ensures that a user has a correct CSRF token.
func RequireCSRF(route string) func(*fiber.Ctx) error {
	return func(ctx *fiber.Ctx) error {
		cfg := services.Get(ctx).Config.Get()

		if cfg.Security.CSRFEnabled {
			return csrfMiddleware(ctx)
		}

		return ctx.Next()
	}
}
