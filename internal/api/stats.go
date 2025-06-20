package api

import "github.com/gofiber/fiber/v2"

func (a *api) registerStats(api fiber.Router) {
	api.Get("/stats", a.handleStats)
}

func (a *api) handleStats(ctx *fiber.Ctx) error {
	// stats, err := a.svc.Stats.GetStats()
	// if err != nil {
	// 	a.logger.Error("Failed to retrieve stats", "error", err)
	// 	return ctx.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
	// 		"error": "Failed to retrieve stats",
	// 	})
	// }

	// return ctx.JSON(stats)
	return nil
}
