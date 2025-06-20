package main

import (
	"context"

	"github.com/lb-selfbot/backend/internal/config"
	"github.com/lb-selfbot/backend/internal/cron"
	"github.com/lb-selfbot/backend/internal/database"
	"github.com/lb-selfbot/backend/internal/logger"
	"github.com/lb-selfbot/backend/internal/repositories"
	"github.com/lb-selfbot/backend/internal/server"
	"github.com/lb-selfbot/backend/internal/services"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())
	logger := logger.Get("main")

	cfgProvider, err := config.NewProvider()
	if err != nil {
		logger.Error("Failed to load configuration", "error", err)
		cancel()
		return
	}

	database := database.New()
	if err := database.Connect(ctx); err != nil {
		logger.Error("Failed to connect to database", "error", err)
		cancel()
		return
	}

	repos := repositories.New(database.Client())

	svc := services.New(cfgProvider, repos)

	scheduler := cron.NewScheduler(database.Client())
	if err := scheduler.Setup(); err != nil {
		logger.Error("Failed to setup cron scheduler", "error", err)
		cancel()
		return
	}

	srv := server.New(cfgProvider.Get(), svc)
	if err := srv.Start(ctx); err != nil {
		logger.Error("Failed to start server", "error", err)
		cancel()
		return
	}
}
