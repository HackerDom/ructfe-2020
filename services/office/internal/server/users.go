package server

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/HackerDom/ructfe2020/internal/manager"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/go-chi/chi"
	"github.com/golang/protobuf/jsonpb"
	"io/ioutil"
	"net/http"
)

type users struct {
	s *usersService
}

var marshaler = jsonpb.Marshaler{}

func (s *users) handleListUsers(w http.ResponseWriter, _ *http.Request) {
	users, err := s.s.List(context.Background(), &pb.ListRequest{
		Offset: 0,
		Limit:  0,
	})
	if err != nil {
		_, _ = fmt.Fprintf(w, err.Error())
	}
	_ = marshaler.Marshal(w, users)
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
	us, err := s.s.Register(context.Background(), &pb.RegisterRequest{Name: u.Name})
	_ = marshaler.Marshal(w, us)
}

func (s *users) Register(mux *chi.Mux) {
	mux.Post("/users/register", s.registerUser)
	mux.Get("/users", s.handleListUsers)
}

type usersService struct {
	m *manager.Manager
}

func (s *usersService) List(c context.Context, req *pb.ListRequest) (*pb.ListResponse, error) {
	names, err := s.m.GetUsers()
	if err != nil {
		return nil, err
	}
	return &pb.ListResponse{Usernames: names}, nil
}

func (s *usersService) Register(c context.Context, req *pb.RegisterRequest) (*pb.RegisterResponse, error) {
	u, err := s.m.RegisterUser(req.Name)
	if err != nil {
		return nil, err
	}
	return &pb.RegisterResponse{
		User: u,
	}, nil
}