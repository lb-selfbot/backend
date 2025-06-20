package middleware

import (
	"slices"
	"strings"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/compress"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/csrf"
	"github.com/gofiber/fiber/v2/middleware/helmet"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/lb-selfbot/backend/internal/errors"
	"github.com/lb-selfbot/backend/internal/services"
)

func Register(app *fiber.App, svc *services.Services) {
	cfg := svc.Config.Get()

	corsConfig := cors.Config{
		AllowOrigins:     strings.Join(cfg.CORS.AllowOrigins, ", "),
		AllowCredentials: true,
	}

	csrfConfig := csrf.Config{
		Next: func(ctx *fiber.Ctx) bool {
			// This CSRF middleware is only used for setting the token, so it should
			// only run on "safe" methods.
			switch ctx.Method() {
			case fiber.MethodGet, fiber.MethodHead, fiber.MethodOptions, fiber.MethodTrace:
				return false
			default:
				return true
			}
		},
		CookieSameSite: "Strict",
		Storage:        csrfStorage,
	}

	app.Use(compress.New())
	app.Use(helmet.New())
	// app.Use(favicon.New(faviconConfig))
	app.Use(logger.New())
	app.Use(cors.New(corsConfig))
	app.Use(contextMiddleware(svc))
	// app.Use(hostMiddleware())
	app.Use(csrf.New(csrfConfig))
	app.Use(authMiddleware(svc.Auth))
}

// contextMiddleware sets the services in the context for later use in handlers.
func contextMiddleware(svc *services.Services) fiber.Handler {
	return func(ctx *fiber.Ctx) error {
		svc.Store(ctx)

		return ctx.Next()
	}
}

// hostMiddleware checks if the request is coming from an allowed host.
func hostMiddleware() fiber.Handler {
	return func(ctx *fiber.Ctx) error {
		cfg := services.Get(ctx).Config.Get()

		hostname := ctx.Hostname()

		if !slices.Contains(cfg.CORS.AllowOrigins, hostname) {
			return errors.ErrHostNotAllowed
		}

		return ctx.Next()
	}
}
