package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/pkg/eval"
	"io"
	"net/http"

	"github.com/go-chi/chi"
	"github.com/go-chi/chi/middleware"
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
	mux.Use(middleware.Logger)
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

func (s *server) handleRand(w http.ResponseWriter, _ *http.Request) {
	_, _ = fmt.Fprintf(w, hashutil.RandDigest("some random text"))
}

func (s *server) handleEval(w http.ResponseWriter, r *http.Request) {
	expr := chi.URLParam(r, "expr")
	res, err := eval.Eval(expr, make(map[string]string))
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
	mux.HandleFunc("/", s.handleHello)
	mux.HandleFunc("/users", s.handleListUsers)
	mux.HandleFunc("/rand", s.handleRand)
	mux.HandleFunc("/eval/{expr}", s.handleEval)
}
