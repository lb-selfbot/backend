package api

import (
	"github.com/gofiber/fiber/v2"
	"github.com/lb-selfbot/backend/internal/middleware"
	"github.com/lb-selfbot/backend/internal/services/auth"
	"github.com/lb-selfbot/backend/internal/utils"
)

func (a *api) registerAuth(router fiber.Router) {
	router.Post("/login", middleware.MustCaptcha(), a.handleLogin)
	router.Post("/register", middleware.MustCaptcha(), a.registerHandler)
	router.Post("/refresh", a.refreshTokenHandler)
	router.Post("/logout", a.logoutHandler)
	router.Post("/logout-all", middleware.MustAuth(), a.logoutAllHandler)
	router.Post("/forgot-password", middleware.MustCaptcha(), a.handleForgotPassword)
}

type loginRequest struct {
	Username string `json:"username" validate:"required"`
	Password string `json:"password" validate:"required"`
}

func (a *api) handleLogin(ctx *fiber.Ctx) error {
	var req loginRequest
	if err := utils.ParseBody(ctx, &req); err != nil {
		return err
	}

	sessionInfo := auth.SessionInfo{
		IPAddress: ctx.IP(),
		UserAgent: ctx.Get("User-Agent"),
	}

	response, err := a.svc.Auth.Login(req.Username, req.Password, sessionInfo)
	if err != nil {
		a.logger.Warn("Login failed", "username", req.Username, "error", err)
		return ctx.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
			"error": "Invalid credentials",
		})
	}

	return ctx.JSON(response)
}

type registerRequest struct {
	Username string `json:"username" validate:"required,min=3,max=50"`
	Email    string `json:"email" validate:"email"`
	Password string `json:"password" validate:"required,min=8"`
}

func (a *api) registerHandler(ctx *fiber.Ctx) error {
	var req registerRequest
	if err := utils.ParseBody(ctx, &req); err != nil {
		return err
	}

	sessionInfo := auth.SessionInfo{
		IPAddress: ctx.IP(),
		UserAgent: ctx.Get("User-Agent"),
	}

	registerData := auth.RegisterData{
		Username: req.Username,
		Email:    req.Email,
		Password: req.Password,
	}

	response, err := a.svc.Auth.Register(registerData, sessionInfo)
	if err != nil {
		a.logger.Warn("Registration failed", "username", req.Username, "error", err)
		return ctx.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": err.Error(),
		})
	}

	return ctx.Status(fiber.StatusCreated).JSON(response)
}

type refreshTokenRequest struct {
	RefreshToken string `json:"refresh_token" validate:"required"`
}

func (a *api) refreshTokenHandler(ctx *fiber.Ctx) error {
	var req refreshTokenRequest
	if err := utils.ParseBody(ctx, &req); err != nil {
		return err
	}

	sessionInfo := auth.SessionInfo{
		IPAddress: ctx.IP(),
		UserAgent: ctx.Get("User-Agent"),
	}

	response, err := a.svc.Auth.RefreshToken(req.RefreshToken, sessionInfo)
	if err != nil {
		a.logger.Warn("Token refresh failed", "error", err)
		return ctx.Status(fiber.StatusUnauthorized).JSON(fiber.Map{
			"error": "Invalid or expired refresh token",
		})
	}

	return ctx.JSON(response)
}

func (a *api) logoutHandler(ctx *fiber.Ctx) error {
	var req refreshTokenRequest
	if err := utils.ParseBody(ctx, &req); err != nil {
		return err
	}

	err := a.svc.Auth.RevokeRefreshToken(req.RefreshToken)
	if err != nil {
		a.logger.Warn("Logout failed", "error", err)
		return ctx.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to logout",
		})
	}

	return ctx.JSON(fiber.Map{
		"message": "Successfully logged out",
	})
}

func (a *api) logoutAllHandler(ctx *fiber.Ctx) error {
	userID := middleware.GetClaims(ctx).UserID

	err := a.svc.Auth.RevokeAllUserTokens(userID)
	if err != nil {
		a.logger.Warn("Logout all failed", "userID", userID, "error", err)
		return ctx.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
			"error": "Failed to logout from all devices",
		})
	}

	return ctx.JSON(fiber.Map{
		"message": "Successfully logged out from all devices",
	})
}

type forgotPasswordRequest struct {
	Username string `json:"username" validate:"required"`
}

func (a *api) handleForgotPassword(ctx *fiber.Ctx) error {
	var req forgotPasswordRequest
	if err := utils.ParseBody(ctx, &req); err != nil {
		return err
	}

	user, err := a.svc.Auth.GetUserByUsername(req.Username)
	if err != nil {
		return err
	}

	if user.Email == "" {
		return ctx.Status(fiber.StatusBadRequest).JSON(fiber.Map{
			"error": "User does not have an email associated",
		})
	}

	// TODO: send email

	return nil
}
