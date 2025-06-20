package middleware

import (
	"github.com/gofiber/fiber/v2"
	"github.com/lb-selfbot/backend/internal/services"
	"github.com/valyala/fasthttp"
)

const siteverifyURL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

type captchaRequest struct {
	Token string `json:"cf-turnstile-response" validate:"required"`
}

type captchaResponse struct {
	Success bool `json:"success"`
}

func MustCaptcha() fiber.Handler {
	return func(ctx *fiber.Ctx) error {
		svc := services.Get(ctx)
		cfg := svc.Config.Get()

		if !cfg.Security.CaptchaEnabled {
			return ctx.Next()
		}

		var req captchaRequest
		if err := ctx.BodyParser(&req); err != nil {
			return err
		}

		args := fasthttp.AcquireArgs()
		defer fasthttp.ReleaseArgs(args)

		args.Set("secret", cfg.Security.CaptchaSecret)
		args.Set("response", req.Token)
		args.Set("remoteip", ctx.Get("CF-Connecting-IP"))

		statusCode, body, err := fasthttp.Post(nil, siteverifyURL, args)
		if err != nil || statusCode != fiber.StatusOK {
			return ctx.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to verify captcha",
			})
		}

		var resp captchaResponse
		if err := ctx.App().Config().JSONDecoder(body, &resp); err != nil {
			return ctx.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
				"error": "Failed to decode captcha response",
			})
		}

		if !resp.Success {
			return ctx.Status(fiber.StatusBadRequest).JSON(fiber.Map{
				"error": "Captcha verification failed",
			})
		}

		return ctx.Next()
	}
}
