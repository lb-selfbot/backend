package config

import "time"

// Data holds all configuration for the LightningBot backend
type Data struct {
	// Server configuration
	Server ServerConfig `yaml:"server" json:"server"`

	// Database configuration
	Database DatabaseConfig `yaml:"database" json:"database"`

	// Security configuration
	Security SecurityConfig `yaml:"security" json:"security"`

	// Email configuration
	Email EmailConfig `yaml:"email" json:"email"`

	// Redis configuration (optional, for caching/sessions)
	Redis RedisConfig `yaml:"redis" json:"redis"`

	// Logging configuration
	Logging LoggingConfig `yaml:"logging" json:"logging"`

	// CORS configuration
	CORS CORSConfig `yaml:"cors" json:"cors"`

	// Application-specific settings
	App AppConfig `yaml:"app" json:"app"`

	// Third-party integrations
	Integrations IntegrationsConfig `yaml:"integrations" json:"integrations"`
}

// ServerConfig holds HTTP server configuration
type ServerConfig struct {
	Host         string        `yaml:"host" json:"host"`                   // Server host (default: "0.0.0.0")
	Port         int           `yaml:"port" json:"port"`                   // Server port (default: 8080)
	ReadTimeout  time.Duration `yaml:"read_timeout" json:"read_timeout"`   // Request read timeout
	WriteTimeout time.Duration `yaml:"write_timeout" json:"write_timeout"` // Response write timeout
	IdleTimeout  time.Duration `yaml:"idle_timeout" json:"idle_timeout"`   // Connection idle timeout
	Prefork      bool          `yaml:"prefork" json:"prefork"`             // Enable prefork mode for performance
	BodyLimit    int           `yaml:"body_limit" json:"body_limit"`       // Max body size in bytes

	// TLS Configuration
	TLS TLSConfig `yaml:"tls" json:"tls"`
}

// TLSConfig holds TLS/SSL configuration
type TLSConfig struct {
	Enabled  bool   `yaml:"enabled" json:"enabled"`     // Enable HTTPS
	CertFile string `yaml:"cert_file" json:"cert_file"` // Path to certificate file
	KeyFile  string `yaml:"key_file" json:"key_file"`   // Path to private key file
	AutoTLS  bool   `yaml:"auto_tls" json:"auto_tls"`   // Enable automatic TLS via Let's Encrypt
}

// DatabaseConfig holds database connection configuration
type DatabaseConfig struct {
	Driver   string `yaml:"driver" json:"driver"`     // Database driver (sqlite3, mysql, postgres)
	Host     string `yaml:"host" json:"host"`         // Database host
	Port     int    `yaml:"port" json:"port"`         // Database port
	Name     string `yaml:"name" json:"name"`         // Database name
	Username string `yaml:"username" json:"username"` // Database username
	Password string `yaml:"password" json:"password"` // Database password

	// Connection pool settings
	MaxOpenConns    int           `yaml:"max_open_conns" json:"max_open_conns"`         // Maximum open connections
	MaxIdleConns    int           `yaml:"max_idle_conns" json:"max_idle_conns"`         // Maximum idle connections
	ConnMaxLifetime time.Duration `yaml:"conn_max_lifetime" json:"conn_max_lifetime"`   // Connection max lifetime
	ConnMaxIdleTime time.Duration `yaml:"conn_max_idle_time" json:"conn_max_idle_time"` // Connection max idle time

	// SQLite specific
	SQLitePath string `yaml:"sqlite_path" json:"sqlite_path"` // Path to SQLite database file

	// Migration settings
	AutoMigrate bool `yaml:"auto_migrate" json:"auto_migrate"` // Run migrations on startup
}

// SecurityConfig holds security-related configuration
type SecurityConfig struct {
	JWTSecret         string        `yaml:"jwt_secret" json:"jwt_secret"`                   // JWT signing secret
	JWTExpiration     time.Duration `yaml:"jwt_expiration" json:"jwt_expiration"`           // JWT token expiration
	RefreshExpiration time.Duration `yaml:"refresh_expiration" json:"refresh_expiration"`   // Refresh token expiration
	PasswordMinLength int           `yaml:"password_min_length" json:"password_min_length"` // Minimum password length
	BcryptCost        int           `yaml:"bcrypt_cost" json:"bcrypt_cost"`                 // Bcrypt hashing cost
	RateLimitEnabled  bool          `yaml:"rate_limit_enabled" json:"rate_limit_enabled"`   // Enable rate limiting
	RateLimitRequests int           `yaml:"rate_limit_requests" json:"rate_limit_requests"` // Requests per window
	RateLimitWindow   time.Duration `yaml:"rate_limit_window" json:"rate_limit_window"`     // Rate limit window
	CSRFEnabled       bool          `yaml:"csrf_enabled" json:"csrf_enabled"`               // Enable CSRF protection
	CSRFSecret        string        `yaml:"csrf_secret" json:"csrf_secret"`                 // CSRF secret key
	CaptchaEnabled    bool          `yaml:"captcha_enabled" json:"captcha_enabled"`         // Enable captcha verification
	CaptchaSecret     string        `yaml:"captcha_secret" json:"captcha_secret"`           // Captcha secret key (e.g., Cloudflare Turnstile)
	CaptchaSiteKey    string        `yaml:"captcha_sitekey" json:"captcha_sitekey"`         // Captcha site key for client-side integration
	TrustedProxies    []string      `yaml:"trusted_proxies" json:"trusted_proxies"`         // Trusted proxy IPs
}

// EmailConfig holds email service configuration
type EmailConfig struct {
	Enabled   bool   `yaml:"enabled" json:"enabled"`       // Enable email functionality
	SMTPHost  string `yaml:"smtp_host" json:"smtp_host"`   // SMTP server host
	SMTPPort  int    `yaml:"smtp_port" json:"smtp_port"`   // SMTP server port
	Username  string `yaml:"username" json:"username"`     // SMTP username
	Password  string `yaml:"password" json:"password"`     // SMTP password
	FromEmail string `yaml:"from_email" json:"from_email"` // Default from email address
	FromName  string `yaml:"from_name" json:"from_name"`   // Default from name
	UseTLS    bool   `yaml:"use_tls" json:"use_tls"`       // Use TLS encryption
	UseSSL    bool   `yaml:"use_ssl" json:"use_ssl"`       // Use SSL encryption

	// Email templates
	Templates EmailTemplatesConfig `yaml:"templates" json:"templates"`
}

// EmailTemplatesConfig holds email template configuration
type EmailTemplatesConfig struct {
	PasswordResetSubject string `yaml:"password_reset_subject" json:"password_reset_subject"`
	PasswordResetBody    string `yaml:"password_reset_body" json:"password_reset_body"`
	WelcomeSubject       string `yaml:"welcome_subject" json:"welcome_subject"`
	WelcomeBody          string `yaml:"welcome_body" json:"welcome_body"`
}

// RedisConfig holds Redis configuration
type RedisConfig struct {
	Enabled  bool   `yaml:"enabled" json:"enabled"`   // Enable Redis
	Host     string `yaml:"host" json:"host"`         // Redis host
	Port     int    `yaml:"port" json:"port"`         // Redis port
	Password string `yaml:"password" json:"password"` // Redis password
	Database int    `yaml:"database" json:"database"` // Redis database number

	// Connection pool settings
	MaxRetries    int           `yaml:"max_retries" json:"max_retries"`         // Maximum retry attempts
	MinIdleConns  int           `yaml:"min_idle_conns" json:"min_idle_conns"`   // Minimum idle connections
	PoolSize      int           `yaml:"pool_size" json:"pool_size"`             // Connection pool size
	PoolTimeout   time.Duration `yaml:"pool_timeout" json:"pool_timeout"`       // Pool timeout
	IdleTimeout   time.Duration `yaml:"idle_timeout" json:"idle_timeout"`       // Idle connection timeout
	IdleCheckFreq time.Duration `yaml:"idle_check_freq" json:"idle_check_freq"` // Idle check frequency
}

// LoggingConfig holds logging configuration
type LoggingConfig struct {
	Level      string `yaml:"level" json:"level"`             // Log level (debug, info, warn, error)
	Format     string `yaml:"format" json:"format"`           // Log format (json, text)
	Output     string `yaml:"output" json:"output"`           // Log output (stdout, stderr, file)
	FilePath   string `yaml:"file_path" json:"file_path"`     // Log file path (if output is file)
	MaxSize    int    `yaml:"max_size" json:"max_size"`       // Max log file size in MB
	MaxBackups int    `yaml:"max_backups" json:"max_backups"` // Max backup files to keep
	MaxAge     int    `yaml:"max_age" json:"max_age"`         // Max age of log files in days
	Compress   bool   `yaml:"compress" json:"compress"`       // Compress old log files
}

// CORSConfig holds CORS configuration
type CORSConfig struct {
	Enabled          bool     `yaml:"enabled" json:"enabled"`                     // Enable CORS
	AllowOrigins     []string `yaml:"allow_origins" json:"allow_origins"`         // Allowed origins
	AllowMethods     []string `yaml:"allow_methods" json:"allow_methods"`         // Allowed HTTP methods
	AllowHeaders     []string `yaml:"allow_headers" json:"allow_headers"`         // Allowed headers
	ExposeHeaders    []string `yaml:"expose_headers" json:"expose_headers"`       // Headers to expose
	AllowCredentials bool     `yaml:"allow_credentials" json:"allow_credentials"` // Allow credentials
	MaxAge           int      `yaml:"max_age" json:"max_age"`                     // Preflight cache duration
}

// AppConfig holds application-specific configuration
type AppConfig struct {
	Name        string `yaml:"name" json:"name"`               // Application name
	Version     string `yaml:"version" json:"version"`         // Application version
	Environment string `yaml:"environment" json:"environment"` // Environment (development, staging, production)
	Debug       bool   `yaml:"debug" json:"debug"`             // Debug mode

	// Feature flags
	Features FeatureFlags `yaml:"features" json:"features"`

	// License key settings
	LicenseKey LicenseKeyConfig `yaml:"license_key" json:"license_key"`
}

// FeatureFlags holds feature toggle configuration
type FeatureFlags struct {
	Registration      bool `yaml:"registration" json:"registration"`             // Allow new user registration
	PasswordReset     bool `yaml:"password_reset" json:"password_reset"`         // Enable password reset
	EmailVerification bool `yaml:"email_verification" json:"email_verification"` // Require email verification
	TwoFactorAuth     bool `yaml:"two_factor_auth" json:"two_factor_auth"`       // Enable 2FA
	API               bool `yaml:"api" json:"api"`                               // Enable API endpoints
	WebSocket         bool `yaml:"websocket" json:"websocket"`                   // Enable WebSocket connections
	FileUpload        bool `yaml:"file_upload" json:"file_upload"`               // Enable file uploads
	Backup            bool `yaml:"backup" json:"backup"`                         // Enable database backups
}

// LicenseKeyConfig holds license key configuration
type LicenseKeyConfig struct {
	DefaultDuration time.Duration `yaml:"default_duration" json:"default_duration"` // Default license duration
	MaxDuration     time.Duration `yaml:"max_duration" json:"max_duration"`         // Maximum license duration
	AllowRenewal    bool          `yaml:"allow_renewal" json:"allow_renewal"`       // Allow license renewal
	GracePeriod     time.Duration `yaml:"grace_period" json:"grace_period"`         // Grace period after expiration
}

// IntegrationsConfig holds third-party integration configuration
type IntegrationsConfig struct {
	SendGrid  SendGridConfig  `yaml:"sendgrid" json:"sendgrid"`   // SendGrid for emails
	Discord   DiscordConfig   `yaml:"discord" json:"discord"`     // Discord integration
	Stripe    StripeConfig    `yaml:"stripe" json:"stripe"`       // Stripe for payments
	Analytics AnalyticsConfig `yaml:"analytics" json:"analytics"` // Analytics services
}

// SendGridConfig holds SendGrid configuration
type SendGridConfig struct {
	Enabled bool   `yaml:"enabled" json:"enabled"` // Enable SendGrid
	APIKey  string `yaml:"api_key" json:"api_key"` // SendGrid API key
}

// DiscordConfig holds Discord integration configuration
type DiscordConfig struct {
	Enabled      bool   `yaml:"enabled" json:"enabled"`             // Enable Discord integration
	BotToken     string `yaml:"bot_token" json:"bot_token"`         // Discord bot token
	ClientID     string `yaml:"client_id" json:"client_id"`         // Discord application client ID
	ClientSecret string `yaml:"client_secret" json:"client_secret"` // Discord application client secret
	GuildID      string `yaml:"guild_id" json:"guild_id"`           // Discord guild (server) ID
}

// StripeConfig holds Stripe configuration
type StripeConfig struct {
	Enabled        bool   `yaml:"enabled" json:"enabled"`                 // Enable Stripe integration
	SecretKey      string `yaml:"secret_key" json:"secret_key"`           // Stripe secret key
	PublishableKey string `yaml:"publishable_key" json:"publishable_key"` // Stripe publishable key
	WebhookSecret  string `yaml:"webhook_secret" json:"webhook_secret"`   // Stripe webhook secret
}

// AnalyticsConfig holds analytics configuration
type AnalyticsConfig struct {
	Enabled    bool   `yaml:"enabled" json:"enabled"`         // Enable analytics
	Provider   string `yaml:"provider" json:"provider"`       // Analytics provider (google, mixpanel, etc.)
	TrackingID string `yaml:"tracking_id" json:"tracking_id"` // Analytics tracking ID
	APIKey     string `yaml:"api_key" json:"api_key"`         // Analytics API key
}
