package cron

import (
	"log/slog"

	"github.com/go-co-op/gocron/v2"
	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/internal/cron/jobs"
	"github.com/lb-selfbot/backend/internal/logger"
)

type Scheduler interface {
	Setup() error

	Shutdown() error
}

type scheduler struct {
	logger    *slog.Logger
	client    *ent.Client
	scheduler gocron.Scheduler
}

func NewScheduler(client *ent.Client) Scheduler {
	return &scheduler{
		logger: logger.Get("cron"),
		client: client,
	}
}

func (s *scheduler) Setup() error {
	var err error
	s.scheduler, err = gocron.NewScheduler()
	if err != nil {
		s.logger.Error("Failed to create scheduler", "error", err)
		return err
	}

	s.createJobs()

	s.scheduler.Start()
	return nil
}

func (s *scheduler) createJobs() {
	// Run password reset token cleanup once at startup and then daily at midnight
	jobs.ClearResetTokens(s.client)
	s.scheduler.NewJob(
		gocron.DailyJob(
			1,
			gocron.NewAtTimes(gocron.NewAtTime(0, 0, 0)),
		),
		gocron.NewTask(jobs.ClearResetTokens, s.client),
	)

	// Run refresh token cleanup once at startup and then daily at midnight
	jobs.ClearExpiredRefreshTokens(s.client)
	s.scheduler.NewJob(
		gocron.DailyJob(
			1,
			gocron.NewAtTimes(gocron.NewAtTime(0, 0, 0)),
		),
		gocron.NewTask(jobs.ClearExpiredRefreshTokens, s.client),
	)
}

func (s *scheduler) Shutdown() error {
	s.logger.Info("Shutting down scheduler")
	return s.scheduler.Shutdown()
}
