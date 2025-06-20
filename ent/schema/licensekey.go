package schema

import (
	"time"

	"entgo.io/ent"
	"entgo.io/ent/schema/edge"
	"entgo.io/ent/schema/field"
)

type LicenseKeyType uint

func (f LicenseKeyType) Has(flag LicenseKeyType) bool { return f&flag != 0 }
func (f *LicenseKeyType) Add(flag LicenseKeyType)     { *f |= flag }
func (f *LicenseKeyType) Clear(flag LicenseKeyType)   { *f &= ^flag }
func (f *LicenseKeyType) Toggle(flag LicenseKeyType)  { *f ^= flag }

const (
	// LicenseKeyLifetime indicated the license key is for lifetime access.
	LicenseKeyLifetime LicenseKeyType = 1 << iota

	// LicenseKeyHosting indicated the license key is for hosting.
	LicenseKeyHosting
)

// LicenseKey holds the schema definition for the LicenseKey entity.
type LicenseKey struct {
	ent.Schema
}

// Fields of the LicenseKey.
func (LicenseKey) Fields() []ent.Field {
	return []ent.Field{
		field.String("key").
			Unique().
			NotEmpty(),

		field.Uint("type").
			Default(uint(LicenseKeyLifetime)),

		field.Int("credit").
			Default(0).
			Comment("In minutes"),

		field.Time("created_at").
			Default(time.Now).
			Immutable(),

		field.Time("redeemed_at").
			Optional(),
	}
}

// Edges of the LicenseKey.
func (LicenseKey) Edges() []ent.Edge {
	return []ent.Edge{
		edge.To("created_by", User.Type).
			Required(),

		edge.From("redeemed_by", User.Type).
			Ref("license_key"),
	}
}
