package relay

import (
	"context"
	"errors"
	"sync"
	"testing"
)

type fakeProducer struct{ msgs []Message }

func (f *fakeProducer) Produce(_ context.Context, m Message) error {
	f.msgs = append(f.msgs, m)
	return nil
}

type fakeDedupe struct {
	seen map[string]bool
	err  error
}

func (f *fakeDedupe) FirstSeen(_ context.Context, id string) (bool, error) {
	if f.err != nil {
		return false, f.err
	}
	if f.seen[id] {
		return false, nil
	}
	f.seen[id] = true
	return true, nil
}

var testTopics = Topics{Events: "evt", DLQ: "dlq"}

const valid = `{"event_id":"e1","timestamp":"t","version":"1","agent_id":"a1","agent_role":"dev","payload":{"x":1}}`

func TestValidEventGoesToEvents(t *testing.T) {
	p := &fakeProducer{}
	r := New(&fakeDedupe{seen: map[string]bool{}}, p, testTopics)
	if err := r.Handle(context.Background(), "office/agents/a1/status", []byte(valid)); err != nil {
		t.Fatal(err)
	}
	m := p.msgs[0]
	if m.Topic != testTopics.Events || m.Key != "a1" || m.Headers["mqtt_topic"] != "office/agents/a1/status" {
		t.Fatalf("unexpected %+v", m)
	}
}

func TestDuplicateIsDropped(t *testing.T) {
	p := &fakeProducer{}
	r := New(&fakeDedupe{seen: map[string]bool{}}, p, testTopics)
	_ = r.Handle(context.Background(), "t", []byte(valid))
	_ = r.Handle(context.Background(), "t", []byte(valid))
	if len(p.msgs) != 1 {
		t.Fatalf("want 1, got %d", len(p.msgs))
	}
}

func TestInvalidGoesToDLQ(t *testing.T) {
	for _, raw := range []string{"not json", `{"event_id":"e"}`, `{}`} {
		p := &fakeProducer{}
		r := New(&fakeDedupe{seen: map[string]bool{}}, p, testTopics)
		if err := r.Handle(context.Background(), "t", []byte(raw)); err != nil {
			t.Fatal(err)
		}
		if p.msgs[0].Topic != testTopics.DLQ || p.msgs[0].Headers["error"] == "" {
			t.Fatalf("not dead-lettered: %q", raw)
		}
	}
}

func TestDedupeFailureStillProduces(t *testing.T) {
	p := &fakeProducer{}
	r := New(&fakeDedupe{err: errors.New("redis down")}, p, testTopics)
	_ = r.Handle(context.Background(), "t", []byte(valid))
	if len(p.msgs) != 1 || p.msgs[0].Topic != testTopics.Events {
		t.Fatal("should produce despite dedupe failure")
	}
}

type lockedDedupe struct {
	mu   sync.Mutex
	seen map[string]bool
}

func (l *lockedDedupe) FirstSeen(_ context.Context, id string) (bool, error) {
	l.mu.Lock()
	defer l.mu.Unlock()
	if l.seen[id] {
		return false, nil
	}
	l.seen[id] = true
	return true, nil
}

type lockedProducer struct {
	mu    sync.Mutex
	count int
}

func (l *lockedProducer) Produce(_ context.Context, _ Message) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	l.count++
	return nil
}

func TestConcurrentDuplicatesProduceOnce(t *testing.T) {
	p := &lockedProducer{}
	r := New(&lockedDedupe{seen: map[string]bool{}}, p, testTopics)
	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_ = r.Handle(context.Background(), "t", []byte(valid))
		}()
	}
	wg.Wait()
	if p.count != 1 {
		t.Fatalf("want 1, got %d", p.count)
	}
}
