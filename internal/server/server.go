package server

import (
	"context"
	"fmt"
	"log/slog"

	"github.com/goccy/go-json"
	"github.com/gofiber/fiber/v2"
	"github.com/lb-selfbot/backend/internal/api"
	"github.com/lb-selfbot/backend/internal/config"
	"github.com/lb-selfbot/backend/internal/logger"
	"github.com/lb-selfbot/backend/internal/middleware"
	"github.com/lb-selfbot/backend/internal/services"
)

type Server interface {
	// Start the server
	Start(context.Context) error

	// Shutdown the server gracefully
	Shutdown() error
}

type server struct {
	logger *slog.Logger

	app *fiber.App
	api api.API

	addr string
}

// New creates a new server instance with the provided configuration.
func New(cfg *config.Data, svc *services.Services) Server {
	s := &server{
		logger: logger.Get("server"),
		addr:   fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port),
	}

	app := fiber.New(fiber.Config{
		AppName:           cfg.App.Name,
		ErrorHandler:      s.errorHandler,
		JSONEncoder:       json.Marshal,
		JSONDecoder:       json.Unmarshal,
		EnablePrintRoutes: true,
	})

	middleware.Register(app, svc)

	s.app = app
	s.api = api.New(app, svc)
	s.api.RegisterRoutes()

	return s
}

func (s *server) errorHandler(ctx *fiber.Ctx, err error) error {
	s.logger.Error("Error occurred while processing request",
		"error", err,
		"method", ctx.Method(),
		"url", ctx.OriginalURL(),
	)

	return err
}

func (s *server) Start(ctx context.Context) error {
	if err := s.app.Listen(s.addr); err != nil {
		s.logger.ErrorContext(ctx, "Failed to start server", "error", err)
		return err
	}
	return nil
}

func (s *server) Shutdown() error {
	if err := s.app.Shutdown(); err != nil {
		s.logger.Error("Failed to shutdown server", "error", err)
		return err
	}
	return nil
}
