package jobs

import (
	"context"
	"time"

	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/ent/passwordresettoken"
	"github.com/lb-selfbot/backend/internal/logger"
)

func ClearResetTokens(client *ent.Client) {
	logger := logger.Get("cron-ClearResetTokens")
	const resetTokenExpiry = 24 * 60 * 60 // 24 hours in seconds

	n, err := client.PasswordResetToken.Delete().Where(
		passwordresettoken.CreatedAtLT(time.Now().Add(-time.Duration(resetTokenExpiry) * time.Second)),
	).Exec(context.Background())
	if err != nil {
		logger.Error("Failed to clear expired password reset tokens", "error", err)
		return
	}

	logger.Info("Cleared expired password reset tokens", "count", n)
}
