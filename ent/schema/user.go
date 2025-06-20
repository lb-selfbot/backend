package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

type UserFlags uint

func (f UserFlags) Has(flag UserFlags) bool { return f&flag != 0 }
func (f *UserFlags) Add(flag UserFlags)     { *f |= flag }
func (f *UserFlags) Clear(flag UserFlags)   { *f &= ^flag }
func (f *UserFlags) Toggle(flag UserFlags)  { *f ^= flag }

const (
	// UserFlagActive indicates the user is active.
	UserFlagActive UserFlags = 1 << iota

	// UserFlagBanned indicates the user is banned.
	UserFlagBanned

	// UserFlagTester indicates the user is a tester.
	UserFlagTester

	// UserFlagAdmin indicates the user is an admin.
	UserFlagAdmin

	// UserFlagHosting indicates the user is hosting.
	UserFlagHosting

	// UserFlagLifetimeHosting indicates the user has lifetime hosting.
	UserFlagLifetimeHosting
)

// User holds the schema definition for the User entity.
type User struct {
	ent.Schema
}

// Fields of the User.
func (User) Fields() []ent.Field {
	return []ent.Field{
		field.String("username").
			Unique().
			NotEmpty(),

		field.String("email").
			Unique().
			Optional(),

		field.String("password_hash").
			NotEmpty(),

		field.Uint("flags").
			Default(uint(UserFlagActive)),

		field.Time("date_joined").
			Default(time.Now),

		field.Time("last_login").
			Optional(),

		field.Time("free_trial_expiry").
			Optional(),

		field.Time("last_selfbot_login").
			Optional(),

		field.Time("last_selfbot_ping").
			Optional(),

		field.Uint("logins").
			Default(0),

		field.Int64("login_time").
			Default(0),

		field.Time("created_at").
			Default(time.Now).
			Immutable(),

		field.Int("hosting_credit").
			Default(0).
			Comment("In minutes"),

		field.String("hosting_token").
			Optional(),
	}
}

// Edges of the User.
func (User) Edges() []ent.Edge {
	return []ent.Edge{
		edge.To("license_key", LicenseKey.Type).
			Unique(),
		edge.To("refresh_tokens", RefreshToken.Type),
	}
}
