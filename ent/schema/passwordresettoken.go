package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

// PasswordResetToken holds the schema definition for the PasswordResetToken entity.
type PasswordResetToken struct {
	ent.Schema
}

// Fields of the PasswordResetToken.
func (PasswordResetToken) Fields() []ent.Field {
	return []ent.Field{
		field.String("token_hash").
			NotEmpty().
			Unique(),

		field.Time("created_at").
			Default(time.Now).
			Immutable(),
	}
}

// Edges of the PasswordResetToken.
func (PasswordResetToken) Edges() []ent.Edge {
	return []ent.Edge{
		edge.To("user", User.Type).
			Required(),
	}
}
