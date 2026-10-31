// Package config carrega a configuração do gateway exclusivamente do ambiente
// (e de um arquivo .env opcional). Não há valores padrão embutidos no código.
package config

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"
)

// Config reúne toda a configuração do gateway.
type Config struct {
	MQTTURL        string
	MQTTClientID   string
	MQTTTopic      string
	MQTTQoS        byte
	KafkaBrokers   []string
	KafkaTopicEvts string
	KafkaTopicDLQ  string
	RedisAddr      string
	DedupeTTL      time.Duration
	DedupePrefix   string
	MetricsAddr    string
}

// LoadDotEnv lê KEY=VALUE de um arquivo e exporta o que ainda não estiver no ambiente.
// Arquivo ausente não é erro (em produção o ambiente já vem preenchido).
func LoadDotEnv(path string) error {
	f, err := os.Open(path)
	if err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	defer f.Close()
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		line := strings.TrimSpace(sc.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		key, value, ok := strings.Cut(line, "=")
		if !ok {
			continue
		}
		key = strings.TrimSpace(key)
		if _, exists := os.LookupEnv(key); !exists {
			_ = os.Setenv(key, strings.Trim(strings.TrimSpace(value), `"'`))
		}
	}
	return sc.Err()
}

// Load valida e monta a configuração; toda variável é obrigatória.
func Load() (Config, error) {
	var missing []string
	get := func(key string) string {
		v := os.Getenv(key)
		if v == "" {
			missing = append(missing, key)
		}
		return v
	}
	cfg := Config{
		MQTTURL:        get("MQTT_URL"),
		MQTTClientID:   get("MQTT_CLIENT_ID"),
		MQTTTopic:      get("MQTT_SUBSCRIBE_TOPIC"),
		KafkaTopicEvts: get("KAFKA_TOPIC_EVENTS"),
		KafkaTopicDLQ:  get("KAFKA_TOPIC_DLQ"),
		RedisAddr:      get("REDIS_ADDR"),
		DedupePrefix:   get("DEDUPE_KEY_PREFIX"),
		MetricsAddr:    get("METRICS_ADDR"),
	}
	brokers, qos, ttl := get("KAFKA_BROKERS"), get("MQTT_QOS"), get("DEDUPE_TTL")
	if len(missing) > 0 {
		return Config{}, fmt.Errorf("variáveis de ambiente ausentes: %s", strings.Join(missing, ", "))
	}
	cfg.KafkaBrokers = strings.Split(brokers, ",")
	q, err := strconv.Atoi(qos)
	if err != nil || q < 0 || q > 2 {
		return Config{}, fmt.Errorf("MQTT_QOS inválido: %q (use 0, 1 ou 2)", qos)
	}
	cfg.MQTTQoS = byte(q)
	if cfg.DedupeTTL, err = time.ParseDuration(ttl); err != nil {
		return Config{}, fmt.Errorf("DEDUPE_TTL inválido: %w", err)
	}
	return cfg, nil
}
