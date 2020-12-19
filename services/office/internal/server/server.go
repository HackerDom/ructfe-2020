package server

import (
	"github.com/HackerDom/ructfe2020/internal/hashutil"
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/HackerDom/ructfe2020/pkg/eval"
	pb "github.com/HackerDom/ructfe2020/proto"

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
	m *manager.Manager
}

func New(m *manager.Manager) *server {
	return &server{m: m, usersService: NewUsers(m)}
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

func (s *server) handleHello(w http.ResponseWriter, r *http.Request) {
	_, _ = fmt.Fprintf(w, "Hello World!")
}

func (s *server) handleRand(w http.ResponseWriter, r *http.Request) {
	text := chi.URLParam(r, "text")
	_, _ = fmt.Fprintf(w, hashutil.RandDigest(text))
}

func (s *server) handleEval(w http.ResponseWriter, r *http.Request) {
	expr := chi.URLParam(r, "expr")
	res, err := eval.Eval(expr, map[string]string{"secret": "lol_wow"}, make([]*pb.User, 0))
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

func (s *server) Register(mux *chi.Mux) {
	mux.Use(middleware.RequestID)
	mux.Use(middleware.RealIP)
	mux.Use(middleware.Logger)
	mux.Use(middleware.Recoverer)

	// mount controllers
	s.usersService.Mount(mux)

	mux.HandleFunc("/", s.handleHello)
	mux.HandleFunc("/rand/{text}", s.handleRand)
	mux.HandleFunc("/eval/{expr}", s.handleEval)
}
