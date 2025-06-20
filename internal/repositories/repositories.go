package repositories

import "github.com/lb-selfbot/backend/ent"

type Repositories struct {
	User UserRepository
}

func New(client *ent.Client) *Repositories {
	return &Repositories{
		User: NewUserRepository(client),
	}
}
