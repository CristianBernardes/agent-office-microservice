package config

import (
	"os"
	"path/filepath"
	"testing"
	"time"
)

var keys = []string{
	"MQTT_URL", "MQTT_CLIENT_ID", "MQTT_SUBSCRIBE_TOPIC", "MQTT_QOS", "KAFKA_BROKERS",
	"KAFKA_TOPIC_EVENTS", "KAFKA_TOPIC_DLQ", "REDIS_ADDR", "DEDUPE_TTL", "DEDUPE_KEY_PREFIX",
}

func setAll(t *testing.T) {
	for _, k := range keys {
		t.Setenv(k, "x")
	}
	t.Setenv("MQTT_QOS", "1")
	t.Setenv("DEDUPE_TTL", "24h")
	t.Setenv("KAFKA_BROKERS", "a:1,b:2")
}

func TestLoadOK(t *testing.T) {
	setAll(t)
	cfg, err := Load()
	if err != nil || cfg.MQTTQoS != 1 || cfg.DedupeTTL != 24*time.Hour || len(cfg.KafkaBrokers) != 2 {
		t.Fatalf("unexpected %+v %v", cfg, err)
	}
}

func TestLoadMissingListsKeys(t *testing.T) {
	setAll(t)
	t.Setenv("REDIS_ADDR", "")
	if _, err := Load(); err == nil {
		t.Fatal("expected error")
	}
}

func TestLoadInvalidQoSAndTTL(t *testing.T) {
	setAll(t)
	t.Setenv("MQTT_QOS", "9")
	if _, err := Load(); err == nil {
		t.Fatal("expected qos error")
	}
	t.Setenv("MQTT_QOS", "1")
	t.Setenv("DEDUPE_TTL", "abc")
	if _, err := Load(); err == nil {
		t.Fatal("expected ttl error")
	}
}

func TestLoadDotEnvDoesNotOverrideEnvironment(t *testing.T) {
	t.Setenv("FROM_ENV", "env")
	path := filepath.Join(t.TempDir(), ".env")
	_ = os.WriteFile(path, []byte("# c\nFROM_ENV=file\nNEW_KEY=\"v\"\n"), 0o600)
	t.Cleanup(func() { _ = os.Unsetenv("NEW_KEY") })
	if err := LoadDotEnv(path); err != nil {
		t.Fatal(err)
	}
	if os.Getenv("FROM_ENV") != "env" || os.Getenv("NEW_KEY") != "v" {
		t.Fatal("dotenv precedence broken")
	}
	if err := LoadDotEnv(filepath.Join(t.TempDir(), "nope")); err != nil {
		t.Fatal("missing file must be ok")
	}
}
