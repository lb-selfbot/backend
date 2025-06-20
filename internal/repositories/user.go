package repositories

import (
	"context"
	"errors"
	"time"

	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/ent/user"
)

type GetUserArgs struct {
	ID       int
	Username string
}

type UserRepository interface {
	// Create creates a new user in the database.
	Create(ctx context.Context, username, pwdHash string) (*ent.User, error)

	// Get retrieves a user by either ID or Username.
	Get(ctx context.Context, args GetUserArgs) (*ent.User, error)

	// Exists checks if a user exists by ID or Username.
	Exists(ctx context.Context, args GetUserArgs) (bool, error)

	// AddLogin adds a login to a user.
	AddLogin(ctx context.Context, userID int) (*ent.User, error)
}

type userRepository struct {
	client *ent.Client
}

func NewUserRepository(client *ent.Client) UserRepository {
	return &userRepository{
		client: client,
	}
}

func (r *userRepository) Create(ctx context.Context, username, pwdHash string) (*ent.User, error) {
	if username == "" || pwdHash == "" {
		return nil, errors.New("username and password hash cannot be empty")
	}

	return r.client.User.Create().
		SetUsername(username).
		SetPasswordHash(pwdHash).
		Save(ctx)
}

func (r *userRepository) Get(ctx context.Context, args GetUserArgs) (*ent.User, error) {
	if args.ID != 0 {
		return r.client.User.Get(ctx, args.ID)
	}
	if args.Username != "" {
		return r.client.User.Query().Where(user.UsernameEQ(args.Username)).Only(ctx)
	}
	return nil, errors.New("either ID or Username must be provided to get a user")
}

func (r *userRepository) Exists(ctx context.Context, args GetUserArgs) (bool, error) {
	query := r.client.User.Query()

	if args.ID != 0 {
		return query.Where(user.IDEQ(args.ID)).Exist(ctx)
	}

	if args.Username != "" {
		return query.Where(user.UsernameEQ(args.Username)).Exist(ctx)
	}

	return false, errors.New("either ID or Username must be provided to check user existence")
}

func (r *userRepository) AddLogin(ctx context.Context, userID int) (*ent.User, error) {
	return r.client.User.UpdateOneID(userID).
		SetLastLogin(time.Now()).
		AddLogins(1).
		Save(ctx)
}
