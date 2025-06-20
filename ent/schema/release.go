package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/schema/field"
)

type ReleaseComponent uint

const (
	// ReleaseComponentSelfbot indicates the release is for Selfbot.
	ReleaseComponentSelfbot ReleaseComponent = iota
)

// Release holds the schema definition for the Release entity.
type Release struct {
	ent.Schema
}

// Fields of the Release.
func (Release) Fields() []ent.Field {
	return []ent.Field{
		field.Uint("component"),

		field.String("version").
			Unique().
			NotEmpty(),

		field.String("changelog").
			Optional(),

		field.String("uuid").
			Unique().
			NotEmpty(),

		field.Time("created_at").
			Default(time.Now).
			Immutable(),
	}
}

// Edges of the Release.
func (Release) Edges() []ent.Edge {
	return nil
}
