package main

import (
	"context"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	"github.com/redis/go-redis/v9"
	"github.com/segmentio/kafka-go"

	"github.com/CristianBernardes/agent-office-microservice/gateway/internal/relay"
)

func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

type redisDeduper struct{ client *redis.Client }

func (d redisDeduper) FirstSeen(ctx context.Context, id string) (bool, error) {
	return d.client.SetNX(ctx, "gw:event:"+id, 1, 24*time.Hour).Result()
}

type kafkaProducer struct{ writer *kafka.Writer }

func (p kafkaProducer) Produce(ctx context.Context, m relay.Message) error {
	headers := make([]kafka.Header, 0, len(m.Headers))
	for k, v := range m.Headers {
		headers = append(headers, kafka.Header{Key: k, Value: []byte(v)})
	}
	return p.writer.WriteMessages(ctx, kafka.Message{
		Topic: m.Topic, Key: []byte(m.Key), Value: m.Value, Headers: headers,
	})
}

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	writer := &kafka.Writer{
		Addr:     kafka.TCP(strings.Split(env("KAFKA_BROKERS", "localhost:9092"), ",")...),
		Balancer: &kafka.Hash{},
	}
	defer writer.Close()
	rdb := redis.NewClient(&redis.Options{Addr: env("REDIS_ADDR", "localhost:6379")})
	r := relay.New(redisDeduper{rdb}, kafkaProducer{writer})

	opts := mqtt.NewClientOptions().
		AddBroker(env("MQTT_URL", "tcp://localhost:1883")).
		SetClientID("agent-office-gateway").
		SetAutoReconnect(true).
		SetCleanSession(false)
	opts.OnConnect = func(c mqtt.Client) {
		token := c.Subscribe("office/#", 1, func(_ mqtt.Client, m mqtt.Message) {
			if err := r.Handle(ctx, m.Topic(), m.Payload()); err != nil {
				log.Printf("relay error on %s: %v", m.Topic(), err)
			}
		})
		token.Wait()
		log.Printf("subscribed to office/# (err=%v)", token.Error())
	}
	client := mqtt.NewClient(opts)
	if t := client.Connect(); t.Wait() && t.Error() != nil {
		log.Fatalf("mqtt connect: %v", t.Error())
	}
	<-ctx.Done()
	client.Disconnect(250)
}
