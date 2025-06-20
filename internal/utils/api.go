package utils

import (
	"github.com/go-playground/validator/v10"
	"github.com/gofiber/fiber/v2"
)

var validate = validator.New()

// ParseBody is a utility function to parse and validate the request body.
func ParseBody(c *fiber.Ctx, dest any) error {
	if err := c.BodyParser(dest); err != nil {
		return fiber.NewError(fiber.StatusBadRequest, "Invalid request body")
	}

	if err := validate.Struct(dest); err != nil {
		return fiber.NewError(fiber.StatusBadRequest, "Invalid request body")
	}

	return nil
}
