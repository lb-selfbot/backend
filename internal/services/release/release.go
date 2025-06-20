package release

import (
	"context"

	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/ent/release"
	"github.com/lb-selfbot/backend/ent/schema"
)

type Service interface {
	GetLatest(component schema.ReleaseComponent) (*ent.Release, error)
}

type service struct {
	db database.Service
}

// NewService creates a new release service instance.
func NewService(db database.Service) Service {
	return &service{
		db: db,
	}
}

func (s *service) GetLatest(component schema.ReleaseComponent) (*ent.Release, error) {
	release, err := s.db.Client().Release.Query().
		Where(release.ComponentEQ(uint(component))).
		Order(release.ByCreatedAt()).
		First(context.Background())
	if err != nil {
		return nil, err
	}
	return release, nil
}
