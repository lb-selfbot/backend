package jobs

import (
	"context"
	"time"

	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/ent/refreshtoken"
	"github.com/lb-selfbot/backend/internal/logger"
)

func ClearExpiredRefreshTokens(client *ent.Client) {
	logger := logger.Get("cron-ClearExpiredRefreshTokens")

	// Delete tokens that are either expired or revoked and older than 7 days
	cutoff := time.Now().Add(-7 * 24 * time.Hour)

	n, err := client.RefreshToken.Delete().Where(
		refreshtoken.Or(
			refreshtoken.ExpiresAtLT(time.Now()),
			refreshtoken.And(
				refreshtoken.RevokedEQ(true),
				refreshtoken.CreatedAtLT(cutoff),
			),
		),
	).Exec(context.Background())
	if err != nil {
		logger.Error("Failed to clear expired refresh tokens", "error", err)
		return
	}

	if n > 0 {
		logger.Info("Cleared expired refresh tokens", "count", n)
	}
}
