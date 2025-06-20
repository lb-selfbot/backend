package database

import (
	"context"
	"log/slog"

	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/internal/logger"
)

type Database interface {
	// Connect establishes a connection to the database.
	Connect(ctx context.Context) error

	// Client returns the Ent client for database operations.
	Client() *ent.Client
}

type database struct {
	logger *slog.Logger

	client *ent.Client
}

func New() Database {
	return &database{
		logger: logger.Get("database"),
	}
}

func (d *database) Connect(ctx context.Context) error {
	var err error
	d.client, err = ent.Open("sqlite3", "file:ent.db?mode=memory&cache=shared&_fk=1")
	if err != nil {
		d.logger.Error("Failed to connect to database", "error", err)

		return err
	}
	return d.client.Schema.Create(ctx)
}

func (d *database) Client() *ent.Client {
	if d.client == nil {
		d.logger.Error("Database client is not initialized")
		return nil
	}
	return d.client
}
