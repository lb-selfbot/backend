package services

import (
	"github.com/gofiber/fiber/v2"
	"github.com/lb-selfbot/backend/internal/config"
	"github.com/lb-selfbot/backend/internal/repositories"
	"github.com/lb-selfbot/backend/internal/services/auth"
	"github.com/lb-selfbot/backend/internal/services/release"
)

const ctxKey = "svc"

type Services struct {
	Auth    auth.Service
	Release release.Service
}

// New creates a new Services instance with all required services initialized.
func New(cfgProvider config.Provider, repos *repositories.Repositories) *Services {
	svc := &Services{}

	svc.Auth = auth.NewService(cfgProvider, repos)
	svc.Release = release.NewService(repos)

	return svc
}

// Store sets the Services instance in the Fiber context.
func (s *Services) Store(ctx *fiber.Ctx) {
	ctx.Locals(ctxKey, s)
}

// Get retrieves the Services instance from the Fiber context.
func Get(ctx *fiber.Ctx) *Services {
	return ctx.Locals(ctxKey).(*Services)
}
