package server

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/manager"
	"github.com/go-chi/chi"
	"io"
	"io/ioutil"
	"net/http"
)

type users struct {
	m *manager.Manager
}

func (s *users) handleListUsers(w http.ResponseWriter, _ *http.Request) {
	users, err := json.Marshal(s.m.GetUsers())
	if err != nil {
		_, _ = fmt.Fprintf(w, err.Error())
	}
	_, _ = io.Copy(w, bytes.NewBuffer(users))
}

func (s *users) registerUser(w http.ResponseWriter, r *http.Request) {
	j, err := ioutil.ReadAll(r.Body)
	if err != nil {
		handleErr(w, err)
		return
	}
	type user struct {
		Name string `json:"name"`
	}
	u := &user{}
	err = json.Unmarshal(j, u)
	if err != nil {
		handleErr(w, err)
		return
	}
	token := s.m.RegisterUser(u.Name)
	_, _ = fmt.Fprintf(w, token)
}

func (s *users) Register(mux *chi.Mux) {
	mux.Post("/users/register", s.registerUser)
	mux.Get("/users", s.handleListUsers)
}
