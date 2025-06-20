package auth

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"log/slog"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/lb-selfbot/backend/ent"
	"github.com/lb-selfbot/backend/ent/passwordresettoken"
	"github.com/lb-selfbot/backend/ent/refreshtoken"
	"github.com/lb-selfbot/backend/ent/user"
	"github.com/lb-selfbot/backend/internal/config"
	"github.com/lb-selfbot/backend/internal/logger"
	"github.com/lb-selfbot/backend/internal/repositories"
)

type LoginResponse struct {
	User         *ent.User `json:"user"`
	AccessToken  string    `json:"access_token"`
	RefreshToken string    `json:"refresh_token"`
}

type RegisterData struct {
	Username string `json:"username"`
	Email    string `json:"email"`
	Password string `json:"password"`
}

type RegisterResponse struct {
	User         *ent.User `json:"user"`
	AccessToken  string    `json:"access_token"`
	RefreshToken string    `json:"refresh_token"`
}

type RefreshTokenRequest struct {
	RefreshToken string `json:"refresh_token"`
}

type RefreshTokenResponse struct {
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
}

type TokenPair struct {
	AccessToken  string
	RefreshToken string
}

type SessionInfo struct {
	IPAddress string
	UserAgent string
}

type Claims struct {
	UserID   int    `json:"user_id"`
	Username string `json:"username"`

	jwt.RegisteredClaims
}

type Service interface {
	// Login authenticates a user with the provided username and password.
	Login(username, password string, sessionInfo SessionInfo) (*LoginResponse, error)

	// Register creates a new user account.
	Register(data RegisterData, sessionInfo SessionInfo) (*RegisterResponse, error)

	// RefreshToken generates a new access token using a refresh token.
	RefreshToken(refreshToken string, sessionInfo SessionInfo) (*RefreshTokenResponse, error)

	// RevokeRefreshToken revokes a specific refresh token.
	RevokeRefreshToken(refreshToken string) error

	// RevokeAllUserTokens revokes all refresh tokens for a user.
	RevokeAllUserTokens(userID int) error

	// ValidateAccessToken validates and parses an access token.
	ValidateAccessToken(token string) (*Claims, error)

	// CleanupExpiredTokens removes expired refresh tokens.
	CleanupExpiredTokens() error

	// GetUserByID retrieves a user by their ID.
	GetUserByID(userID int) (*ent.User, error)

	// GetUserByUsername retrieves a user by their username.
	GetUserByUsername(username string) (*ent.User, error)

	// CreatePasswordResetToken creates a password reset token for a user.
	CreatePasswordResetToken(userID int) (string, error)

	// ValidatePasswordResetToken validates a password reset token.
	ValidatePasswordResetToken(token string) (bool, error)
}

type service struct {
	logger *slog.Logger

	config config.Provider
	repos  *repositories.Repositories
}

func NewService(config config.Provider, repos *repositories.Repositories) Service {
	return &service{
		logger: logger.Get("auth"),
		config: config,
		repos:  repos,
	}
}

func (s *service) Login(username, password string, sessionInfo SessionInfo) (*LoginResponse, error) {
	user, err := s.repos.User.Get(context.Background(), repositories.GetUserArgs{Username: username})
	if err != nil {
		return nil, fmt.Errorf("user not found")
	}

	if !VerifyArgon2(password, user.PasswordHash) {
		return nil, fmt.Errorf("invalid password")
	}

	// Update last login
	user, err = s.repos.User.AddLogin(context.Background(), user.ID)
	if err != nil {
		s.logger.Warn("Failed to update user login info", "error", err)
	}

	// Generate token pair
	tokenPair, err := s.generateTokenPair(user, sessionInfo)
	if err != nil {
		return nil, fmt.Errorf("failed to generate tokens: %w", err)
	}

	// Remove password hash from response
	userResponse := *user
	userResponse.PasswordHash = ""

	return &LoginResponse{
		User:         &userResponse,
		AccessToken:  tokenPair.AccessToken,
		RefreshToken: tokenPair.RefreshToken,
	}, nil
}

func (s *service) Register(data RegisterData, sessionInfo SessionInfo) (*RegisterResponse, error) {
	// Check if user already exists
	exists, err := s.repos.User.Exists(context.Background(), repositories.GetUserArgs{Username: data.Username})
	if err != nil {
		return nil, fmt.Errorf("failed to check user existence: %w", err)
	}

	if exists {
		return nil, fmt.Errorf("username already exists")
	}

	// Hash password
	passwordHash, err := HashArgon2(data.Password)
	if err != nil {
		return nil, fmt.Errorf("failed to hash password: %w", err)
	}

	// Create user
	user, err := s.repos.User.Create(context.Background(), data.Username, passwordHash)
	if err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	// Generate token pair
	tokenPair, err := s.generateTokenPair(user, sessionInfo)
	if err != nil {
		return nil, fmt.Errorf("failed to generate tokens: %w", err)
	}

	return &RegisterResponse{
		User:         user,
		AccessToken:  tokenPair.AccessToken,
		RefreshToken: tokenPair.RefreshToken,
	}, nil
}

func (s *service) RefreshToken(refreshTokenStr string, sessionInfo SessionInfo) (*RefreshTokenResponse, error) {
	// Find and validate refresh token
	token, err := s.db.RefreshToken.Query().
		Where(
			refreshtoken.TokenEQ(refreshTokenStr),
			refreshtoken.RevokedEQ(false),
			refreshtoken.ExpiresAtGT(time.Now()),
		).
		WithUser().
		Only(context.Background())
	if err != nil {
		return nil, fmt.Errorf("invalid or expired refresh token")
	}

	// Update last used
	_, err = s.db.RefreshToken.UpdateOneID(token.ID).
		SetLastUsedAt(time.Now()).
		Save(context.Background())
	if err != nil {
		s.logger.Warn("Failed to update refresh token last used", "error", err)
	}

	// Generate new token pair
	tokenPair, err := s.generateTokenPair(token.Edges.User, sessionInfo)
	if err != nil {
		return nil, fmt.Errorf("failed to generate new tokens: %w", err)
	}

	// Optionally revoke the old refresh token (rotate tokens)
	_, err = s.db.RefreshToken.UpdateOneID(token.ID).
		SetRevoked(true).
		SetRevokedAt(time.Now()).
		Save(context.Background())
	if err != nil {
		s.logger.Warn("Failed to revoke old refresh token", "error", err)
	}

	return &RefreshTokenResponse{
		AccessToken:  tokenPair.AccessToken,
		RefreshToken: tokenPair.RefreshToken,
	}, nil
}

func (s *service) RevokeRefreshToken(refreshTokenStr string) error {
	_, err := s.db.RefreshToken.Update().
		Where(refreshtoken.TokenEQ(refreshTokenStr)).
		SetRevoked(true).
		SetRevokedAt(time.Now()).
		Save(context.Background())

	return err
}

func (s *service) RevokeAllUserTokens(userID int) error {
	_, err := s.db.RefreshToken.Update().
		Where(refreshtoken.UserIDEQ(userID)).
		SetRevoked(true).
		SetRevokedAt(time.Now()).
		Save(context.Background())

	return err
}

func (s *service) ValidateAccessToken(tokenStr string) (*Claims, error) {
	cfg := s.config.Get()

	token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(token *jwt.Token) (any, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(cfg.Security.JWTSecret), nil
	})
	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims, nil
	}

	return nil, fmt.Errorf("invalid token")
}

func (s *service) CleanupExpiredTokens() error {
	_, err := s.db.RefreshToken.Delete().
		Where(refreshtoken.ExpiresAtLT(time.Now())).
		Exec(context.Background())

	return err
}

func (s *service) GetUserByID(userID int) (*ent.User, error) {
	return s.db.User.Get(context.Background(), userID)
}

func (s *service) GetUserByUsername(username string) (*ent.User, error) {
	user, err := s.db.User.Query().
		Where(user.UsernameEQ(username)).
		Only(context.Background())
	if err != nil {
		return nil, fmt.Errorf("user not found")
	}

	return user, nil
}

func (s *service) CreatePasswordResetToken(userID int) (string, error) {
	// Generate secure random token
	tokenBytes := make([]byte, 32)
	_, err := rand.Read(tokenBytes)
	if err != nil {
		return "", err
	}

	tokenStr := hex.EncodeToString(tokenBytes)

	tokenHash := sha256.Sum256(tokenBytes)
	tokenHashStr := hex.EncodeToString(tokenHash[:])

	// Save reset token to database
	_, err = s.db.PasswordResetToken.Create().
		SetTokenHash(tokenHashStr).
		AddUserIDs(userID).
		Save(context.Background())
	if err != nil {
		return "", err
	}

	return tokenStr, nil
}

func (s *service) ValidatePasswordResetToken(token string) (bool, error) {
	tokenBytes, err := hex.DecodeString(token)
	if err != nil {
		return false, err
	}

	// Hash the provided token
	tokenHash := sha256.Sum256(tokenBytes)
	tokenHashStr := hex.EncodeToString(tokenHash[:])

	// todo: does the token belong to the right user
	n, err := s.db.PasswordResetToken.Delete().Where(
		passwordresettoken.TokenHashEQ(tokenHashStr),
		passwordresettoken.CreatedAtGT(time.Now().Add(-24*time.Hour)),
	).Exec(context.Background())
	if err != nil {
		return false, err
	}

	return n > 0, nil
}

// Helper methods

func (s *service) generateTokenPair(user *ent.User, sessionInfo SessionInfo) (*TokenPair, error) {
	// Generate access token
	accessToken, err := s.generateAccessToken(user)
	if err != nil {
		return nil, err
	}

	// Generate refresh token
	refreshToken, err := s.generateRefreshToken(user, sessionInfo)
	if err != nil {
		return nil, err
	}

	return &TokenPair{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
	}, nil
}

func (s *service) generateAccessToken(user *ent.User) (string, error) {
	cfg := s.config.Get()

	claims := Claims{
		UserID:   user.ID,
		Username: user.Username,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    cfg.App.Name,
			Subject:   fmt.Sprintf("%d", user.ID),
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(cfg.Security.JWTExpiration)),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			NotBefore: jwt.NewNumericDate(time.Now()),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(cfg.Security.JWTSecret))
}

func (s *service) generateRefreshToken(user *ent.User, sessionInfo SessionInfo) (string, error) {
	cfg := s.config.Get()

	// Generate secure random token
	tokenBytes := make([]byte, 32)
	_, err := rand.Read(tokenBytes)
	if err != nil {
		return "", err
	}
	tokenStr := hex.EncodeToString(tokenBytes)

	// Save refresh token to database
	_, err = s.db.RefreshToken.Create().
		SetToken(tokenStr).
		SetUserID(user.ID).
		SetExpiresAt(time.Now().Add(cfg.Security.RefreshExpiration)).
		SetIPAddress(sessionInfo.IPAddress).
		SetUserAgent(sessionInfo.UserAgent).
		Save(context.Background())
	if err != nil {
		return "", err
	}

	return tokenStr, nil
}
