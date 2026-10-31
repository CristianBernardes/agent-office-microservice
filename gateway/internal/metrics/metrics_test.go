package metrics

import (
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHandlerExposesCounters(t *testing.T) {
	r := New()
	r.Inc("gateway_produced_total", "office.events")
	r.Inc("gateway_produced_total", "office.events")
	r.Inc("gateway_produce_errors_total", "office.events.dlq")
	rec := httptest.NewRecorder()
	r.Handler().ServeHTTP(rec, httptest.NewRequest("GET", "/metrics", nil))
	body := rec.Body.String()
	if !strings.Contains(body, `gateway_produced_total{topic="office.events"} 2`) ||
		!strings.Contains(body, `gateway_produce_errors_total{topic="office.events.dlq"} 1`) {
		t.Fatalf("unexpected body: %s", body)
	}
}
