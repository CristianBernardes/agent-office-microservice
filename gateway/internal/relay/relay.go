// Package relay contém o núcleo do gateway: valida envelopes, deduplica e roteia.
package relay

import (
	"context"
	"encoding/json"
	"fmt"
)

const (
	TopicEvents = "office.events"
	TopicDLQ    = "office.events.dlq"
)

// Message é uma mensagem pronta para o Kafka.
type Message struct {
	Topic   string
	Key     string
	Value   []byte
	Headers map[string]string
}

// Deduper informa se um event_id é inédito (e o marca como visto).
type Deduper interface {
	FirstSeen(ctx context.Context, eventID string) (bool, error)
}

// Producer publica no Kafka.
type Producer interface {
	Produce(ctx context.Context, msg Message) error
}

type envelope struct {
	EventID   string          `json:"event_id"`
	Timestamp string          `json:"timestamp"`
	AgentID   string          `json:"agent_id"`
	Payload   json.RawMessage `json:"payload"`
}

func (e envelope) validate() error {
	switch {
	case e.EventID == "":
		return fmt.Errorf("missing event_id")
	case e.Timestamp == "":
		return fmt.Errorf("missing timestamp")
	case e.AgentID == "":
		return fmt.Errorf("missing agent_id")
	case len(e.Payload) == 0:
		return fmt.Errorf("missing payload")
	}
	return nil
}

// Relay encaminha mensagens MQTT para o Kafka.
type Relay struct {
	dedupe   Deduper
	producer Producer
}

func New(dedupe Deduper, producer Producer) *Relay {
	return &Relay{dedupe: dedupe, producer: producer}
}

// Handle processa uma mensagem MQTT. Envelopes inválidos vão para a DLQ.
func (r *Relay) Handle(ctx context.Context, mqttTopic string, raw []byte) error {
	var env envelope
	if err := json.Unmarshal(raw, &env); err != nil {
		return r.deadLetter(ctx, mqttTopic, raw, "invalid json: "+err.Error())
	}
	if err := env.validate(); err != nil {
		return r.deadLetter(ctx, mqttTopic, raw, err.Error())
	}
	if r.dedupe != nil {
		first, err := r.dedupe.FirstSeen(ctx, env.EventID)
		// Falha do dedupe: prefere duplicata a perda.
		if err == nil && !first {
			return nil
		}
	}
	return r.producer.Produce(ctx, Message{
		Topic:   TopicEvents,
		Key:     env.AgentID,
		Value:   raw,
		Headers: map[string]string{"mqtt_topic": mqttTopic, "event_id": env.EventID},
	})
}

func (r *Relay) deadLetter(ctx context.Context, mqttTopic string, raw []byte, reason string) error {
	return r.producer.Produce(ctx, Message{
		Topic:   TopicDLQ,
		Value:   raw,
		Headers: map[string]string{"mqtt_topic": mqttTopic, "error": reason},
	})
}
