package server

import (
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/pkg/eval"

	"github.com/go-chi/chi"
	"github.com/go-chi/chi/middleware"

	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

const (
	Port = "8080"
	Addr = "[::]"
)

type server struct {
	m *manager.Manager
}

func New(m *manager.Manager) *server {
	return &server{m: m}
}

func RunServer() error {
	mux := chi.NewMux()
	Register(mux)
	return Serve(mux)
}

func Serve(mux *chi.Mux) error {
	return http.ListenAndServe(fmt.Sprintf("%s:%s", Addr, Port), mux)
}

func (s *server) handleHello(w http.ResponseWriter, r *http.Request) {
	_, _ = fmt.Fprintf(w, "Hello World!")
}

func (s *server) handleListUsers(w http.ResponseWriter, _ *http.Request) {
	users, err := json.Marshal(s.m.GetUsers())
	if err != nil {
		_, _ = fmt.Fprintf(w, err.Error())
	}
	_, _ = io.Copy(w, bytes.NewBuffer(users))
}

func (s *server) handleRand(w http.ResponseWriter, r *http.Request) {
	text := chi.URLParam(r, "text")
	_, _ = fmt.Fprintf(w, hashutil.RandDigest(text))
}

func (s *server) handleEval(w http.ResponseWriter, r *http.Request) {
	expr := chi.URLParam(r, "expr")
	res, err := eval.Eval(expr, map[string]string{"secret": "lol_wow"})
	if err != nil {
		handleErr(w, err)
		return
	}
	_, _ = fmt.Fprintf(w, "%t", res)
}

func handleErr(w http.ResponseWriter, err error) {
	w.WriteHeader(500)
	_, _ = w.Write([]byte(err.Error()))
}

func Register(mux *chi.Mux) {
	s := &server{}

	mux.Use(middleware.RequestID)
	mux.Use(middleware.RealIP)
	mux.Use(middleware.Logger)
	mux.Use(middleware.Recoverer)

	mux.HandleFunc("/", s.handleHello)
	mux.HandleFunc("/users", s.handleListUsers)
	mux.HandleFunc("/rand/{text}", s.handleRand)
	mux.HandleFunc("/eval/{expr}", s.handleEval)
}
