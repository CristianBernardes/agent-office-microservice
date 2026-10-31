// Package metrics expõe contadores do gateway no formato texto do Prometheus,
// sem dependências externas.
package metrics

import (
	"fmt"
	"net/http"
	"sort"
	"sync"
	"sync/atomic"
)

// Registry guarda contadores rotulados por tópico.
type Registry struct {
	mu       sync.Mutex
	counters map[string]*atomic.Uint64
}

// New cria um registro vazio.
func New() *Registry { return &Registry{counters: map[string]*atomic.Uint64{}} }

// Inc incrementa o contador `name` para o rótulo `topic`.
func (r *Registry) Inc(name, topic string) {
	key := fmt.Sprintf("%s{topic=%q}", name, topic)
	r.mu.Lock()
	c, ok := r.counters[key]
	if !ok {
		c = &atomic.Uint64{}
		r.counters[key] = c
	}
	r.mu.Unlock()
	c.Add(1)
}

// Handler serve as métricas em /metrics.
func (r *Registry) Handler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		r.mu.Lock()
		defer r.mu.Unlock()
		keys := make([]string, 0, len(r.counters))
		for k := range r.counters {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		w.Header().Set("Content-Type", "text/plain; version=0.0.4")
		for _, k := range keys {
			fmt.Fprintf(w, "%s %d\n", k, r.counters[k].Load())
		}
	})
}
