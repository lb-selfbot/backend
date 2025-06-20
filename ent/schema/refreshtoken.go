package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
	"entgo.io/ent/schema/index"
)

// RefreshToken holds the schema definition for the RefreshToken entity.
type RefreshToken struct {
	ent.Schema
}

// Fields of the RefreshToken.
func (RefreshToken) Fields() []ent.Field {
	return []ent.Field{
		field.String("token").
			Unique().
			NotEmpty(),

		field.Int("user_id"),

		field.Time("expires_at"),

		field.Time("created_at").
			Default(time.Now).
			Immutable(),

		field.Time("last_used_at").
			Optional(),

		field.String("ip_address").
			Optional(),

		field.String("user_agent").
			Optional(),

		field.Bool("revoked").
			Default(false),

		field.Time("revoked_at").
			Optional(),
	}
}

// Edges of the RefreshToken.
func (RefreshToken) Edges() []ent.Edge {
	return []ent.Edge{
		edge.From("user", User.Type).
			Ref("refresh_tokens").
			Field("user_id").
			Required().
			Unique(),
	}
}

// Indexes of the RefreshToken.
func (RefreshToken) Indexes() []ent.Index {
	return []ent.Index{
		index.Fields("user_id"),
		index.Fields("expires_at"),
		index.Fields("revoked"),
		index.Fields("token").Unique(),
	}
}
