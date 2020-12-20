package server

import (
	"context"
	"github.com/HackerDom/ructfe2020/internal/manager"
	httprpc "github.com/HackerDom/ructfe2020/pkg/httprtc"
	pb "github.com/HackerDom/ructfe2020/proto"
	"github.com/go-chi/chi"
	"github.com/golang/protobuf/proto"
)

func NewUsers(m *manager.Manager) *usersService {
	return &usersService{m: m}
}

type usersService struct {
	m *manager.Manager
}

func (s *usersService) Mount(mux *chi.Mux) {
	httprpc.New("POST", "/users/register").
		Mount(mux).
		WithJSONPbReader(&pb.RegisterRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.Register(ctx, req.(*pb.RegisterRequest))
		})
	httprpc.New("POST", "/users/list").
		Mount(mux).
		WithJSONPbReader(&pb.ListRequest{}).
		WithJSONPbWriter().
		WithHandler(func(ctx context.Context, req proto.Message) (proto.Message, error) {
			return s.List(ctx, req.(*pb.ListRequest))
		})
}

func (s *usersService) List(ctx context.Context, req *pb.ListRequest) (*pb.ListResponse, error) {
	// TODO: [12/13/20] (vaspahomov): pagination
	names, err := s.m.GetNames()
	if err != nil {
		return nil, err
	}
	return &pb.ListResponse{Usernames: names}, nil
}

func (s *usersService) Register(ctx context.Context, req *pb.RegisterRequest) (*pb.RegisterResponse, error) {
	u, err := s.m.RegisterUser(req.Name)
	if err != nil {
		return nil, err
	}
	return &pb.RegisterResponse{
		User: u,
	}, nil
}