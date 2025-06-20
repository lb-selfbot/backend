package logger

import (
	"log/slog"
	"os"
)

var logger *slog.Logger

func init() {
	logger = slog.New(slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{}))
}

// Get returns the default logger instance.
func Get(name ...string) *slog.Logger {
	if len(name) > 0 {
		return logger.With(slog.String("name", name[0]))
	}
	return logger
}
