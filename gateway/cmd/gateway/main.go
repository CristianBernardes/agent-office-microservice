package main

import (
	"context"
	"log"
	"net/http"
	"os/signal"
	"syscall"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"

	"github.com/CristianBernardes/agent-office-microservice/gateway/internal/config"
	"github.com/CristianBernardes/agent-office-microservice/gateway/internal/metrics"
	"github.com/CristianBernardes/agent-office-microservice/gateway/internal/relay"
)

type redisDeduper struct {
	client *redis.Client
	prefix string
	ttl    time.Duration
}

func (d redisDeduper) FirstSeen(ctx context.Context, id string) (bool, error) {
	return d.client.SetNX(ctx, d.prefix+id, 1, d.ttl).Result()
}

type kafkaProducer struct {
	writer  *kafka.Writer
	metrics *metrics.Registry
}

func (p kafkaProducer) Produce(ctx context.Context, m relay.Message) error {
	headers := make([]kafka.Header, 0, len(m.Headers))
	for k, v := range m.Headers {
		headers = append(headers, kafka.Header{Key: k, Value: []byte(v)})
	}
	err := p.writer.WriteMessages(ctx, kafka.Message{
		Topic: m.Topic, Key: []byte(m.Key), Value: m.Value, Headers: headers,
	})
	if err != nil {
		p.metrics.Inc("gateway_produce_errors_total", m.Topic)
		return err
	}
	p.metrics.Inc("gateway_produced_total", m.Topic)
	return nil
}

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	if err := config.LoadDotEnv(".env"); err != nil {
		log.Fatalf("lendo .env: %v", err)
	}
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("configuração: %v", err)
	}

	writer := &kafka.Writer{Addr: kafka.TCP(cfg.KafkaBrokers...), Balancer: &kafka.Hash{}}
	defer writer.Close()
	rdb := redis.NewClient(&redis.Options{Addr: cfg.RedisAddr})
	deduper := redisDeduper{client: rdb, prefix: cfg.DedupePrefix, ttl: cfg.DedupeTTL}
	topics := relay.Topics{Events: cfg.KafkaTopicEvts, DLQ: cfg.KafkaTopicDLQ}
	reg := metrics.New()
	r := relay.New(deduper, kafkaProducer{writer: writer, metrics: reg}, topics)
	mux := http.NewServeMux()
	mux.Handle("/metrics", reg.Handler())
	go func() {
		if err := http.ListenAndServe(cfg.MetricsAddr, mux); err != nil {
			log.Printf("metrics server: %v", err)
		}
	}()

	opts := mqtt.NewClientOptions().
		AddBroker(cfg.MQTTURL).
		SetClientID(cfg.MQTTClientID).
		SetAutoReconnect(true).
		SetCleanSession(false)
	opts.OnConnect = func(c mqtt.Client) {
		token := c.Subscribe(cfg.MQTTTopic, cfg.MQTTQoS, func(_ mqtt.Client, m mqtt.Message) {
			reg.Inc("gateway_mqtt_received_total", m.Topic())
			if err := r.Handle(ctx, m.Topic(), m.Payload()); err != nil {
				log.Printf("relay error on %s: %v", m.Topic(), err)
			}
		})
		token.Wait()
		log.Printf("subscribed to %s (err=%v)", cfg.MQTTTopic, token.Error())
	}
	client := mqtt.NewClient(opts)
	if t := client.Connect(); t.Wait() && t.Error() != nil {
		log.Fatalf("mqtt connect: %v", t.Error())
	}
	<-ctx.Done()
	client.Disconnect(250)
}
