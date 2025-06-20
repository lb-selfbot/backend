package api

import (
	"log/slog"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/monitor"
	"github.com/lb-selfbot/backend/internal/logger"
	"github.com/lb-selfbot/backend/internal/services"
)

type API interface {
	// RegisterRoutes initializes the routes for the Fiber application.
	RegisterRoutes()
}

type api struct {
	logger *slog.Logger

	app *fiber.App
	svc *services.Services
}

func New(app *fiber.App, svc *services.Services) API {
	return &api{
		logger: logger.Get("api"),
		app:    app,
		svc:    svc,
	}
}

func (a *api) RegisterRoutes() {
	a.app.Get("/api/v4/health", func(c *fiber.Ctx) error {
		return c.SendString("OK")
	})

	api := a.app.Group("/api")
	apiV4 := api.Group("/v4")

	a.registerAuth(apiV4.Group("/auth"))

	a.app.Get("/metrics", monitor.New())
}
