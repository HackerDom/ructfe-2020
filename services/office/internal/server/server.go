package server

import (
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/go-chi/chi"
	"github.com/go-chi/chi/middleware"

	"fmt"
	"net/http"
)

const (
	Port = "8080"
	Addr = "[::]"
)

type server struct {
	*usersService
	*documentsService
	m *manager.Manager
}

func New(m *manager.Manager) *server {
	return &server{m: m, usersService: NewUsers(m), documentsService: NewDocuments(m)}
}

func RunServer(m *manager.Manager) error {
	mux := chi.NewMux()
	s := New(m)
	s.Register(mux)
	return Serve(mux)
}

func Serve(mux *chi.Mux) error {
	return http.ListenAndServe(fmt.Sprintf("%s:%s", Addr, Port), mux)
}

func (s *server) Register(mux *chi.Mux) {
	mux.Use(middleware.RequestID)
	mux.Use(middleware.RealIP)
	mux.Use(middleware.Logger)
	mux.Use(middleware.Recoverer)

	// mount controllers
	s.usersService.Mount(mux)
	s.documentsService.Mount(mux)
}
