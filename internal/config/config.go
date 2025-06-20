package config

import (
	"log/slog"
	"os"
	"sync"

	"github.com/fsnotify/fsnotify"
	"github.com/lb-selfbot/backend/internal/logger"
	"gopkg.in/yaml.v3"
)

const configFilePath = "config.yaml"

type Provider interface {
	Get() *Data
	Reload() error
}

type provider struct {
	logger *slog.Logger
	config *Data
	mutex  sync.RWMutex
}

func NewProvider() (Provider, error) {
	prov := &provider{
		logger: logger.Get("config"),
		config: &Data{},
	}

	if err := prov.loadConfig(); err != nil {
		prov.logger.Error("Failed to load initial configuration", "error", err)
		return nil, err
	}

	go prov.notifier()
	return prov, nil
}

func (p *provider) loadConfig() error {
	p.mutex.Lock()
	defer p.mutex.Unlock()

	// Check if config file exists
	if _, err := os.Stat(configFilePath); os.IsNotExist(err) {
		p.logger.Error("Config file does not exist", "path", configFilePath)
		return err
	}

	data, err := os.ReadFile(configFilePath)
	if err != nil {
		return err
	}

	config := &Data{}
	if err := yaml.Unmarshal(data, config); err != nil {
		return err
	}

	p.config = config
	p.logger.Info("Configuration loaded successfully", "path", configFilePath)

	return nil
}

func (p *provider) notifier() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		p.logger.Error("Failed to create watcher", "error", err)
		return
	}
	defer watcher.Close()

	if err := watcher.Add(configFilePath); err != nil {
		p.logger.Error("Failed to add config file to watcher", "error", err)
		return
	}

	for {
		select {
		case event, ok := <-watcher.Events:
			if !ok {
				return
			}
			if event.Op&fsnotify.Write == fsnotify.Write {
				p.logger.Info("Config file changed, reloading...", "file", event.Name)
				if err := p.loadConfig(); err != nil {
					p.logger.Error("Failed to reload config", "error", err)
				} else {
					p.logger.Info("Config reloaded successfully")
				}
			}
		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}
			p.logger.Error("Config file watcher error", "error", err)
		}
	}
}

func (p *provider) Get() *Data {
	p.mutex.RLock()
	defer p.mutex.RUnlock()
	return p.config
}

func (p *provider) Reload() error {
	return p.loadConfig()
}
