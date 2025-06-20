package errors

import "github.com/gofiber/fiber/v2"

var ErrHostNotAllowed = fiber.NewError(fiber.StatusForbidden, "host not allowed")
